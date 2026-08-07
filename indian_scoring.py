"""
Indian Market Intelligence Engine
Scoring engine, NIFTY100 scanner, FII/DII tracker, daily verdict.
Inspired by pradeepsiddappa/indian-trading-agent.
"""

import calendar
import json
from datetime import date, datetime, timedelta, timezone
from time import time
from typing import Any
from urllib.request import Request, urlopen

import yfinance as yf

# ── NIFTY 100 universe (top 50 by weight for fast scans) ──────────────────────
NIFTY100_TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT",
    "AXISBANK", "WIPRO", "ASIANPAINT", "MARUTI", "TITAN",
    "SUNPHARMA", "BAJFINANCE", "HCLTECH", "ADANIENT", "NTPC",
    "POWERGRID", "TECHM", "ULTRACEMCO", "ONGC", "NESTLEIND",
    "M&M", "JSWSTEEL", "TATASTEEL", "DRREDDY", "CIPLA",
    "BAJAJFINSV", "GRASIM", "INDUSINDBK", "EICHERMOT", "HEROMOTOCO",
    "BRITANNIA", "DIVISLAB", "APOLLOHOSP", "HINDALCO", "COALINDIA",
    "BPCL", "SHREECEM", "TATACONSUM", "ITC", "ADANIPORTS",
    "SBILIFE", "HDFCLIFE", "VEDL", "DABUR", "PIDILITIND",
]

SECTOR_MAP = {
    "RELIANCE": "Energy", "ONGC": "Energy", "BPCL": "Energy", "COALINDIA": "Energy",
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT", "HCLTECH": "IT", "TECHM": "IT",
    "HDFCBANK": "Banking", "ICICIBANK": "Banking", "SBIN": "Banking",
    "AXISBANK": "Banking", "KOTAKBANK": "Banking", "INDUSINDBK": "Banking",
    "HINDUNILVR": "FMCG", "ITC": "FMCG", "NESTLEIND": "FMCG",
    "BRITANNIA": "FMCG", "DABUR": "FMCG", "TATACONSUM": "FMCG",
    "LT": "Capital Goods", "ADANIENT": "Conglomerate",
    "MARUTI": "Auto", "M&M": "Auto", "EICHERMOT": "Auto", "HEROMOTOCO": "Auto",
    "SUNPHARMA": "Pharma", "DRREDDY": "Pharma", "CIPLA": "Pharma", "DIVISLAB": "Pharma",
    "TITAN": "Consumer", "ASIANPAINT": "Consumer", "PIDILITIND": "Consumer",
    "BAJFINANCE": "Finance", "BAJAJFINSV": "Finance", "SBILIFE": "Finance", "HDFCLIFE": "Finance",
    "JSWSTEEL": "Metals", "TATASTEEL": "Metals", "HINDALCO": "Metals", "VEDL": "Metals",
    "NTPC": "Power", "POWERGRID": "Power",
    "GRASIM": "Cement", "ULTRACEMCO": "Cement", "SHREECEM": "Cement",
    "APOLLOHOSP": "Healthcare",
    "BHARTIARTL": "Telecom",
    "ADANIPORTS": "Infra",
}

# ── Cache ─────────────────────────────────────────────────────────────────────
_fii_cache: dict | None = None
_fii_cache_time: float = 0
_FII_CACHE_TTL = 3600  # 1 hour


# ── RSI Calculation ───────────────────────────────────────────────────────────
def compute_rsi(series, period: int = 14) -> float:
    try:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(period).mean().iloc[-1]
        avg_loss = loss.rolling(period).mean().iloc[-1]
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return float(100 - (100 / (1 + rs)))
    except Exception:
        return 50.0


# ── FII/DII Flow ──────────────────────────────────────────────────────────────
def fetch_fii_dii_flow() -> dict[str, Any]:
    """Fetch FII/DII net buy/sell data from NSE India."""
    global _fii_cache, _fii_cache_time
    now = time()
    if _fii_cache is not None and (now - _fii_cache_time) < _FII_CACHE_TTL:
        return _fii_cache

    try:
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        })
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        # Find today's or latest entry
        fii_net = 0.0
        dii_net = 0.0
        trade_date = ""
        for entry in (data if isinstance(data, list) else []):
            category = (entry.get("category") or "").strip().upper()
            net_val = float(entry.get("netVal", 0) or 0)
            if "FII" in category or "FPI" in category:
                fii_net += net_val
            elif "DII" in category:
                dii_net += net_val
            trade_date = entry.get("date", trade_date)

        result = {
            "fii_net": round(fii_net, 2),
            "dii_net": round(dii_net, 2),
            "date": trade_date,
            "fii_status": "Buying" if fii_net > 0 else "Selling",
            "dii_status": "Buying" if dii_net > 0 else "Selling",
        }
        _fii_cache = result
        _fii_cache_time = now
        return result
    except Exception:
        # Return neutral on failure
        return {"fii_net": 0.0, "dii_net": 0.0, "date": "", "fii_status": "Unknown", "dii_status": "Unknown"}


# ── F&O Expiry & High-Risk Day Check ─────────────────────────────────────────
def is_high_risk_day() -> tuple[bool, str]:
    """Check if today is a high-risk trading day for Indian markets."""
    today = date.today()

    # F&O expiry = last Thursday of the month
    last_day = calendar.monthrange(today.year, today.month)[1]
    thursdays = [
        d for d in range(1, last_day + 1)
        if date(today.year, today.month, d).weekday() == 3
    ]
    last_thursday = max(thursdays) if thursdays else 0
    if today.day == last_thursday:
        return True, "⚠️ F&O Monthly Expiry — avoid new positions"

    # Day before F&O expiry
    if today.day == last_thursday - 1:
        return False, "📅 F&O Expiry tomorrow — trade cautiously"

    # Weekly expiry = every Thursday
    if today.weekday() == 3:
        return False, "📅 Weekly F&O Expiry day"

    # Union Budget (Feb 1)
    if today.month == 2 and today.day == 1:
        return True, "🚨 Union Budget Day — STAND DOWN"

    # RBI MPC meetings (roughly Feb, Apr, Jun, Aug, Oct, Dec — first week)
    if today.day in range(1, 8) and today.month in [2, 4, 6, 8, 10, 12]:
        return False, "🏦 RBI MPC Meeting week — Banking stocks may be volatile"

    return False, ""


def days_until_next_fno_expiry() -> int:
    """Return number of days until the next monthly F&O expiry (last Thursday)."""
    today = date.today()
    for months_ahead in range(0, 3):
        check_month = (today.month + months_ahead - 1) % 12 + 1
        check_year = today.year + (today.month + months_ahead - 1) // 12
        last_day = calendar.monthrange(check_year, check_month)[1]
        thursdays = [
            d for d in range(1, last_day + 1)
            if date(check_year, check_month, d).weekday() == 3
        ]
        if not thursdays:
            continue
        expiry = date(check_year, check_month, max(thursdays))
        if expiry >= today:
            return (expiry - today).days
    return 0


# ── Individual Stock Scorer ───────────────────────────────────────────────────
def score_indian_stock(ticker: str, fii_net: float = 0.0) -> dict[str, Any]:
    """Score a single NSE stock using technical + FII signals."""
    ns_ticker = f"{ticker}.NS"
    try:
        tk = yf.Ticker(ns_ticker)
        hist = tk.history(period="60d")
        if hist.empty or len(hist) < 15:
            return {"ticker": ticker, "score": 0.0, "rating": "Neutral", "probability": "50%", "signals": [], "rsi": 50.0, "error": "No data"}

        close = hist["Close"]
        volume = hist["Volume"]
        today_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2])
        avg_vol = float(volume.rolling(20).mean().iloc[-1])
        today_vol = float(volume.iloc[-1])

        rsi = compute_rsi(close)
        score = 0.0
        signals = []

        # RSI signals
        if rsi < 30:
            score += 1.5
            signals.append("RSI oversold (<30) 🟢")
        elif rsi > 70:
            score -= 1.5
            signals.append("RSI overbought (>70) 🔴")
        elif 40 <= rsi <= 60:
            signals.append("RSI neutral ⚪")

        # Volume spike
        if avg_vol > 0 and today_vol > 2 * avg_vol:
            if today_close > prev_close:
                score += 2.0
                signals.append("Bullish volume spike (>2x avg) 🟢")
            else:
                score -= 2.0
                signals.append("Bearish volume spike (>2x avg) 🔴")

        # Price momentum (3-day)
        if len(close) >= 4:
            mom3 = (today_close - float(close.iloc[-4])) / float(close.iloc[-4]) * 100
            if mom3 > 3:
                score += 1.0
                signals.append(f"3-day momentum +{mom3:.1f}% 🟢")
            elif mom3 < -3:
                score -= 1.0
                signals.append(f"3-day momentum {mom3:.1f}% 🔴")

        # 52-week high/low check
        try:
            high_52w = float(close.rolling(252).max().iloc[-1]) if len(close) >= 252 else float(close.max())
            low_52w = float(close.rolling(252).min().iloc[-1]) if len(close) >= 252 else float(close.min())
            if today_close >= high_52w * 0.98:
                score += 1.5
                signals.append("Near 52-week high 🟢")
            elif today_close <= low_52w * 1.02:
                score -= 1.5
                signals.append("Near 52-week low 🔴")
        except Exception:
            pass

        # FII flow adjustment
        if fii_net < -2000:
            score -= 1.0
            signals.append("FII net selling 🔴")
        elif fii_net > 1000:
            score += 0.5
            signals.append("FII net buying 🟢")

        # Rating
        if score >= 4:
            rating = "Strong Buy"
            badge = "🟢🟢"
        elif score >= 2:
            rating = "Buy"
            badge = "🟢"
        elif score <= -4:
            rating = "Strong Sell"
            badge = "🔴🔴"
        elif score <= -2:
            rating = "Sell"
            badge = "🔴"
        else:
            rating = "Neutral"
            badge = "🟡"

        prob = min(85, max(15, int(50 + score * 4)))
        change_pct = (today_close - prev_close) / prev_close * 100 if prev_close else 0

        return {
            "ticker": ticker,
            "score": round(score, 1),
            "rating": rating,
            "badge": badge,
            "probability": f"{prob}%",
            "signals": signals,
            "rsi": round(rsi, 1),
            "price": round(today_close, 2),
            "change_pct": round(change_pct, 2),
            "sector": SECTOR_MAP.get(ticker, "Other"),
        }
    except Exception as e:
        return {"ticker": ticker, "score": 0.0, "rating": "Neutral", "badge": "🟡", "probability": "50%", "signals": [], "rsi": 50.0, "error": str(e)}


# ── NIFTY 100 Scanner ─────────────────────────────────────────────────────────
def scan_nifty100(fii_net: float = 0.0, limit: int = 15) -> list[dict]:
    """Scan top NIFTY stocks and return top signals sorted by absolute score."""
    results = []
    for ticker in NIFTY100_TICKERS:
        try:
            result = score_indian_stock(ticker, fii_net)
            if "error" not in result and abs(result["score"]) >= 1.5:
                results.append(result)
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


# ── Daily Verdict ─────────────────────────────────────────────────────────────
def generate_daily_verdict(scan_results: list[dict], fii_net: float = 0.0) -> dict[str, Any]:
    """Generate TRADE / SELECTIVE / STAND DOWN verdict."""
    is_risky, risk_reason = is_high_risk_day()

    if is_risky:
        return {
            "verdict": "STAND DOWN",
            "color": "red",
            "emoji": "🔴",
            "reason": risk_reason,
            "top_picks": [],
        }

    strong_buys = [r for r in scan_results if r["rating"] == "Strong Buy"]
    buys = [r for r in scan_results if r["rating"] in ("Buy", "Strong Buy")]
    strong_sells = [r for r in scan_results if r["rating"] == "Strong Sell"]

    # Massive FII selling = caution
    if fii_net < -3000:
        return {
            "verdict": "SELECTIVE",
            "color": "yellow",
            "emoji": "🟡",
            "reason": f"Heavy FII selling (₹{abs(fii_net):.0f} Cr) — trade only top picks",
            "top_picks": [r["ticker"] for r in strong_buys[:2]],
        }

    if len(strong_buys) >= 3 and len(strong_sells) == 0:
        return {
            "verdict": "TRADE",
            "color": "green",
            "emoji": "🟢",
            "reason": f"{len(strong_buys)} strong opportunities detected",
            "top_picks": [r["ticker"] for r in strong_buys[:3]],
        }
    elif len(buys) >= 1:
        return {
            "verdict": "SELECTIVE",
            "color": "yellow",
            "emoji": "🟡",
            "reason": f"Mixed signals — trade only top {min(2, len(buys))} picks",
            "top_picks": [r["ticker"] for r in buys[:2]],
        }
    else:
        return {
            "verdict": "STAND DOWN",
            "color": "red",
            "emoji": "🔴",
            "reason": "No clear edge today — wait for better setup",
            "top_picks": [],
        }


# ── Full Intel Package ────────────────────────────────────────────────────────
def get_full_intel() -> dict[str, Any]:
    """Build the complete Indian Market Intelligence payload for the API."""
    fii_data = fetch_fii_dii_flow()
    fii_net = fii_data.get("fii_net", 0.0)

    scan_results = scan_nifty100(fii_net=fii_net, limit=15)
    verdict = generate_daily_verdict(scan_results, fii_net=fii_net)
    is_risky, risk_reason = is_high_risk_day()
    fno_days = days_until_next_fno_expiry()

    # Sector breakdown
    sector_scores: dict[str, list[float]] = {}
    for r in scan_results:
        sec = r.get("sector", "Other")
        sector_scores.setdefault(sec, []).append(r["score"])
    sector_summary = {
        sec: round(sum(scores) / len(scores), 1)
        for sec, scores in sector_scores.items()
    }

    return {
        "verdict": verdict,
        "fii": fii_data,
        "scan": scan_results,
        "sector_summary": sector_summary,
        "fno_days": fno_days,
        "risk_day": is_risky,
        "risk_reason": risk_reason,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
