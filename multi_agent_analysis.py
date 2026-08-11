"""
Multi-Agent Deep Analysis Pipeline
5-agent LangGraph workflow: TechnicalAnalyst → BullResearcher → BearResearcher → LeadResearcher → Trader
Inspired by TauricResearch/TradingAgents, adapted to use Groq + yfinance.
"""

import json
import os
from datetime import datetime, timezone
from typing import Annotated, Any, TypedDict
import operator

import yfinance as yf

# ── Agent State ───────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    ticker: str
    price_data: str
    technical_report: str
    news_context: str
    bull_thesis: str
    bear_thesis: str
    research_summary: str
    trade_direction: str
    confidence: str
    entry: str
    sl: str
    tp1: str
    tp2: str
    reason: str
    steps_done: Annotated[list[str], operator.add]


# ── Groq helper (uses ANALYZER_GROQ_API_KEY) ─────────────────────────────────
def _call_groq(prompt: str, system: str, model: str = "llama-3.3-70b-versatile") -> str:
    key = os.getenv("ANALYZER_GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    if not key:
        return "Error: No Groq API key configured."
    import requests
    
    models_to_try = [model, "llama-3.1-8b-instant"]
    last_err = ""
    for m in models_to_try:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": m,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=25,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            else:
                last_err = f"Status {resp.status_code}: {resp.text}"
        except Exception as e:
            last_err = str(e)
            
    return f"Error: {last_err}"


# ── RSI helper ────────────────────────────────────────────────────────────────
def _compute_rsi(series, period: int = 14) -> float:
    try:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0).rolling(period).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean().iloc[-1]
        if loss == 0:
            return 100.0
        return float(100 - (100 / (1 + gain / loss)))
    except Exception:
        return 50.0


# ── Agent Nodes ───────────────────────────────────────────────────────────────
def technical_analyst_node(state: AgentState) -> dict:
    ticker = state["ticker"]
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="90d")
        close = hist["Close"]
        volume = hist["Volume"]
        current_price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2])
        change_pct = (current_price - prev_price) / prev_price * 100
        rsi = _compute_rsi(close)
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20
        avg_vol = float(volume.rolling(20).mean().iloc[-1])
        today_vol = float(volume.iloc[-1])
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1.0

        price_data = (
            f"Asset: {ticker}\n"
            f"Price: {current_price:.4f} ({change_pct:+.2f}% today)\n"
            f"RSI(14): {rsi:.1f}\n"
            f"SMA20: {sma20:.4f} | SMA50: {sma50:.4f}\n"
            f"Price vs SMA20: {'above' if current_price > sma20 else 'below'}\n"
            f"Volume ratio vs 20d avg: {vol_ratio:.1f}x\n"
            f"52w range: {float(close.min()):.4f} – {float(close.max()):.4f}"
        )
    except Exception as e:
        price_data = f"Asset: {ticker}\nError fetching data: {str(e)}"
        current_price = 0

    prompt = (
        f"You are a technical analyst. Here is market data:\n\n{price_data}\n\n"
        f"Write a concise technical analysis (150-200 words) covering: trend direction, "
        f"RSI signal, support/resistance, volume analysis, and 1-2 key observations."
    )
    report = _call_groq(prompt, "You are a professional technical analyst. Be precise and data-driven.")
    return {
        "price_data": price_data,
        "technical_report": report,
        "steps_done": ["technical_analyst"],
    }


def bull_researcher_node(state: AgentState) -> dict:
    prompt = (
        f"TECHNICAL ANALYSIS:\n{state['technical_report']}\n\n"
        f"PRICE DATA:\n{state['price_data']}\n\n"
        f"You are a BULLISH equity researcher. Build the STRONGEST possible case for buying {state['ticker']}. "
        f"Find every bullish signal, potential catalyst, and upside argument. "
        f"Write 150-200 words. Be persuasive and specific."
    )
    thesis = _call_groq(prompt, "You are a bullish equity researcher. Find every reason to buy. Be compelling.")
    return {"bull_thesis": thesis, "steps_done": ["bull_researcher"]}


def bear_researcher_node(state: AgentState) -> dict:
    prompt = (
        f"BULL THESIS:\n{state['bull_thesis']}\n\n"
        f"PRICE DATA:\n{state['price_data']}\n\n"
        f"You are a BEARISH equity researcher. DEBUNK the bull thesis. "
        f"Find every risk, weakness, downside scenario, and reason NOT to buy {state['ticker']}. "
        f"Write 150-200 words. Be critical and realistic."
    )
    thesis = _call_groq(prompt, "You are a bearish equity researcher. Challenge every bullish assumption. Be critical.")
    return {"bear_thesis": thesis, "steps_done": ["bear_researcher"]}


def lead_researcher_node(state: AgentState) -> dict:
    prompt = (
        f"BULL THESIS:\n{state['bull_thesis']}\n\n"
        f"BEAR THESIS:\n{state['bear_thesis']}\n\n"
        f"You are the lead research analyst. Objectively synthesize both sides. "
        f"Identify where bulls and bears agree, where they disagree, and what the key deciding factors are. "
        f"Write a balanced 150-200 word research summary."
    )
    summary = _call_groq(prompt, "You are a senior research analyst. Be objective and balanced.")
    return {"research_summary": summary, "steps_done": ["lead_researcher"]}


def trader_node(state: AgentState) -> dict:
    price_data = state.get("price_data", "")
    # Extract current price from price_data string
    current_price_str = ""
    for line in price_data.split("\n"):
        if "Price:" in line:
            current_price_str = line
            break

    prompt = (
        f"RESEARCH SUMMARY:\n{state['research_summary']}\n\n"
        f"PRICE DATA:\n{price_data}\n\n"
        f"You are a professional trader. Based on the research, generate a concrete trade recommendation. "
        f"Output ONLY a valid JSON object (no extra text) with these exact keys:\n"
        f'{{"direction": "BUY|SELL|NEUTRAL", "entry": "price", "sl": "stop_loss", '
        f'"tp1": "target1", "tp2": "target2", "confidence": "percentage like 72%", '
        f'"reason": "one sentence rationale"}}'
    )
    raw = _call_groq(
        prompt,
        "You are a professional trader. Output ONLY valid JSON. No explanation outside the JSON.",
        model="llama-3.3-70b-versatile",
    )
    # Extract JSON
    import re
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            trade = json.loads(match.group())
            return {
                "trade_direction": trade.get("direction", "NEUTRAL"),
                "confidence": trade.get("confidence", "50%"),
                "entry": str(trade.get("entry", "—")),
                "sl": str(trade.get("sl", "—")),
                "tp1": str(trade.get("tp1", "—")),
                "tp2": str(trade.get("tp2", "—")),
                "reason": trade.get("reason", ""),
                "steps_done": ["trader"],
            }
        except json.JSONDecodeError:
            pass
    # Fallback
    return {
        "trade_direction": "NEUTRAL",
        "confidence": "50%",
        "entry": "—",
        "sl": "—",
        "tp1": "—",
        "tp2": "—",
        "reason": "Could not parse trade recommendation.",
        "steps_done": ["trader"],
    }


# ── Graph Builder ─────────────────────────────────────────────────────────────
def build_graph():
    try:
        from langgraph.graph import StateGraph, END
    except ImportError:
        return None

    graph = StateGraph(AgentState)
    graph.add_node("technical_analyst", technical_analyst_node)
    graph.add_node("bull_researcher", bull_researcher_node)
    graph.add_node("bear_researcher", bear_researcher_node)
    graph.add_node("lead_researcher", lead_researcher_node)
    graph.add_node("trader", trader_node)

    graph.set_entry_point("technical_analyst")
    graph.add_edge("technical_analyst", "bull_researcher")
    graph.add_edge("bull_researcher", "bear_researcher")
    graph.add_edge("bear_researcher", "lead_researcher")
    graph.add_edge("lead_researcher", "trader")
    graph.add_edge("trader", END)

    return graph.compile()


# ── Public API ────────────────────────────────────────────────────────────────
def run_deep_analysis(ticker: str) -> dict[str, Any]:
    """
    Run the full 5-agent deep analysis pipeline.
    Returns a dict with all agent outputs or an error.
    """
    app = build_graph()
    if app is None:
        return {"error": "langgraph not installed. Run: pip install langgraph"}

    try:
        initial_state: AgentState = {
            "ticker": ticker,
            "price_data": "",
            "technical_report": "",
            "news_context": "",
            "bull_thesis": "",
            "bear_thesis": "",
            "research_summary": "",
            "trade_direction": "",
            "confidence": "",
            "entry": "",
            "sl": "",
            "tp1": "",
            "tp2": "",
            "reason": "",
            "steps_done": [],
        }
        final_state = app.invoke(initial_state)
        return {
            "ticker": ticker,
            "price_data": final_state.get("price_data", ""),
            "technical_report": final_state.get("technical_report", ""),
            "bull_thesis": final_state.get("bull_thesis", ""),
            "bear_thesis": final_state.get("bear_thesis", ""),
            "research_summary": final_state.get("research_summary", ""),
            "direction": final_state.get("trade_direction", "NEUTRAL"),
            "confidence": final_state.get("confidence", "—"),
            "entry": final_state.get("entry", "—"),
            "sl": final_state.get("sl", "—"),
            "tp1": final_state.get("tp1", "—"),
            "tp2": final_state.get("tp2", "—"),
            "reason": final_state.get("reason", ""),
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}
