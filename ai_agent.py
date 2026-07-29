import json
import os
from datetime import datetime, timezone, timedelta
from html import escape

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

TRADER_LEVEL_PROMPT = (
    "You are a multi-level trading educator. A trade signal is provided below. "
    "You must explain it for THREE trader experience levels.\n\n"
    "Structure your response EXACTLY like this:\n"
    "BEGINNER|<text>\n"
    "INTERMEDIATE|<text>\n"
    "EXPERIENCED|<text>\n\n"
    "BEGINNER: Explain in simplest terms. Define any jargon (pip, stop loss, take profit, leverage, etc.). "
    "Use analogies. Max 3 sentences.\n\n"
    "INTERMEDIATE: Add technical reasoning. Mention support/resistance, trend context, "
    "why the entry/TP/SL levels make sense. Max 3 sentences.\n\n"
    "EXPERIENCED: Advanced context only. Note order flow, liquidity zones, institutional levels, "
    "correlation insights, or market structure implications. Max 3 sentences.\n\n"
    "Signal to explain:\n"
)


def _openai_chat(prompt: str, system_prompt: str | None = None) -> str | None:
    if not OPENAI_API_KEY:
        return None
    try:
        import requests
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "max_tokens": 800,
            },
            timeout=25,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _groq_chat(prompt: str, system_prompt: str | None = None) -> str | None:
    if not GROQ_API_KEY:
        return None
    try:
        import requests
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _best_ai(prompt: str, system_prompt: str | None = None) -> str | None:
    result = _openai_chat(prompt, system_prompt)
    if result:
        return result
    return _groq_chat(prompt, system_prompt)


def enhance_message_for_trader_levels(
    signal_text: str,
    pair: str,
    direction: str,
    entry: str,
    tp1: str,
    tp2: str,
    sl: str,
) -> dict[str, str]:
    """Generate beginner/intermediate/experienced explanations for a trade signal."""
    context = (
        f"Pair: {pair}\n"
        f"Direction: {direction}\n"
        f"Entry: {entry}\n"
        f"TP1: {tp1}\n"
        f"TP2: {tp2}\n"
        f"SL: {sl}\n"
        f"Full Signal:\n{signal_text[:500]}"
    )
    prompt = TRADER_LEVEL_PROMPT + context
    result = _best_ai(prompt, "You are a professional trading educator. Be accurate and helpful.")
    levels = {"beginner": "", "intermediate": "", "experienced": ""}
    if result:
        for line in result.split("\n"):
            line = line.strip()
            if line.upper().startswith("BEGINNER|"):
                levels["beginner"] = line.split("|", 1)[-1].strip()
            elif line.upper().startswith("INTERMEDIATE|"):
                levels["intermediate"] = line.split("|", 1)[-1].strip()
            elif line.upper().startswith("EXPERIENCED|"):
                levels["experienced"] = line.split("|", 1)[-1].strip()
    return levels


def format_trader_level_block(levels: dict[str, str]) -> str:
    """Format the trader level explanations into a message block."""
    parts = []
    if levels.get("beginner"):
        parts.append(f"📘 *For Beginners:* {levels['beginner']}")
    if levels.get("intermediate"):
        parts.append(f"📙 *For Intermediate:* {levels['intermediate']}")
    if levels.get("experienced"):
        parts.append(f"📈 *For Experienced:* {levels['experienced']}")
    if parts:
        return "\n\n" + "\n\n".join(parts)
    return ""


def enhance_forex_message_with_ai(original_message: str, pair: str, direction: str,
                                   entry: str, tp1: str, tp2: str, sl: str) -> str:
    """Add trader-level learning annotations to a forex/crypto signal message."""
    levels = enhance_message_for_trader_levels(
        original_message, pair, direction, entry, tp1, tp2, sl
    )
    level_block = format_trader_level_block(levels)
    if level_block:
        separator = "\n\n━━━━━━━━━━━━━━━━━━"
        educational_tag = "\n\n🧠 *AI Learning Assistant* — _Tailored for your experience level_"
        return original_message + separator + educational_tag + level_block
    return original_message


def _extract_news_context(news_items: list[dict] | None = None) -> str:
    """Turn recent news items into a compact BTC/crypto news context block."""
    if not news_items:
        return ""
    snippets: list[str] = []
    for item in news_items[:4]:
        title = (item.get("title") or item.get("headline") or item.get("name") or "").strip()
        if title:
            snippets.append(title[:140])
    if not snippets:
        return ""
    return "Recent BTC/crypto news context:\n" + "\n".join(f"- {s}" for s in snippets)


def generate_btc_trade_suggestion(current_price: float | None = None) -> str | None:
    """Generate a standalone BTC/USD trade suggestion using AI and news context."""
    price_context = ""
    if current_price:
        price_context = f"Current BTC/USD price: ${current_price:,.2f}"

    news_context = ""
    try:
        import main
        articles = main.fetch_latest_articles("Bitcoin crypto ETF regulation")
        btc_news = []
        for article in articles[:8]:
            title = (article.get("title") or article.get("headline") or "").strip()
            if title:
                text = f"{title} {article.get('description') or ''}".lower()
                if any(k in text for k in ["bitcoin", "btc", "crypto", "etf", "regulation", "inflation", "fed"]):
                    btc_news.append(article)
            if len(btc_news) >= 3:
                break
        news_context = _extract_news_context(btc_news)
    except Exception:
        news_context = ""

    prompt = (
        "You are a crypto trading analyst. Generate a BTC/USD trade suggestion grounded in recent verified news and price action.\n\n"
        f"{price_context}\n\n"
        f"{news_context}\n\n"
        "Based on recent Bitcoin market conditions and the supplied news context, provide:\n"
        "1. Direction (LONG or SHORT)\n"
        "2. Rationale (1 sentence)\n"
        "3. Key support and resistance levels\n"
        "4. Risk management advice\n\n"
        "Format:\n"
        "DIRECTION: <LONG/SHORT>\n"
        "RATIONALE: <1 sentence>\n"
        "SUPPORT: <level>\n"
        "RESISTANCE: <level>\n"
        "ADVICE: <1 sentence>\n\n"
        "Be factual, evidence-based, and concise. Never give financial advice."
    )
    result = _best_ai(prompt, "You are a professional crypto trading analyst.")
    if not result:
        return None
    return result.strip()


def format_btc_signal_block(ai_suggestion: str, price: float | None = None) -> str:
    """Format a BTC analysis block for inclusion in broadcasts."""
    price_line = ""
    if price:
        price_line = f"💰 *Live Price:* ${price:,.2f}\n"

    lines = [
        "₿ *BTC/USD — News-Backed Trade Idea*",
        "━━━━━━━━━━━━━━━━━━",
        f"{price_line}",
        f"📰 *Trade view:*\n{ai_suggestion}",
        "",
        "📘 *Beginner Note:* Bitcoin trades 24/7 on crypto exchanges. "
        "A LONG trade means you expect the price to rise; use a stop-loss to protect risk.",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "🔖 #BTC  #crypto  #Bitcoin  #newsbacked",
        "⚠️ _Not financial advice. Trade at your own risk._",
    ]
    return "\n".join(lines)


def generate_market_education_tip(topic: str = "general") -> str:
    """Generate an educational trading tip using AI."""
    topics = {
        "position_sizing": "position sizing and risk management",
        "support_resistance": "support and resistance levels",
        "trend_following": "trend following strategies",
        "btc_basics": "Bitcoin trading basics and crypto market dynamics",
        "forex_basics": "forex trading basics including pips, lots, and leverage",
        "risk_management": "risk management and stop-loss placement",
        "general": "a general trading tip for beginners",
    }
    selected = topics.get(topic, topics["general"])

    prompt = (
        f"Generate a short educational trading tip about {selected}. "
        "Write it at three levels:\n"
        "BEGINNER: Simple explanation (1 sentence)\n"
        "INTERMEDIATE: Slightly deeper (1 sentence)\n"
        "EXPERIENCED: Advanced insight (1 sentence)\n\n"
        "Format each line as: BEGINNER|<text>"
    )
    result = _best_ai(prompt, "You are a trading educator. Be accurate and clear.")
    if not result:
        return ""

    lines = result.strip().split("\n")
    beginner = ""
    intermediate = ""
    experienced = ""
    for line in lines:
        line = line.strip()
        if line.upper().startswith("BEGINNER|"):
            beginner = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("INTERMEDIATE|"):
            intermediate = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("EXPERIENCED|"):
            experienced = line.split("|", 1)[-1].strip()

    parts = ["🧠 *Daily Trading Tip*"]
    if beginner:
        parts.append(f"📘 *Beginner:* {beginner}")
    if intermediate:
        parts.append(f"📙 *Intermediate:* {intermediate}")
    if experienced:
        parts.append(f"📈 *Experienced:* {experienced}")
    return "\n\n".join(parts)


def analyze_recent_signals_for_improvement(signal_log: list[dict]) -> str | None:
    """Analyze recent trade signals and suggest improvements to the system."""
    if not signal_log:
        return None

    recent = signal_log[-20:]
    summary_lines = []
    for s in recent:
        summary_lines.append(
            f"{s.get('pair', '?')} {s.get('direction', '?')} @ {s.get('entry', '?')} "
            f"[TP1: {s.get('tp1', '?')} TP2: {s.get('tp2', '?')} SL: {s.get('sl', '?')}]"
        )
    summary = "\n".join(summary_lines)

    from datetime import datetime, timezone, timedelta
    today_name = datetime.now(timezone.utc).strftime("%A")
    prompt = (
        "You are an AI trading system optimizer. Review these recent trade signals:\n\n"
        f"{summary}\n\n"
        f"Today is {today_name}. Analyze:\n"
        "1. Are the TP/SL levels appropriately placed?\n"
        "2. Is there good variety across assets (forex, crypto, stocks)?\n"
        "3. Are BTC signals frequent enough?\n"
        "4. How can the signal quality be improved?\n"
        "5. Suggest ONE creative improvement to the Telegram message format/style/design "
        "(emoji usage, layout, structure, colors via unicode, etc.) to make it more "
        "engaging and professional. Be specific.\n\n"
        "Provide 3-4 specific, actionable suggestions. Be concise."
    )
    return _best_ai(prompt, "You are an expert trading system architect.")


def generate_btc_market_update(prices: dict | None = None) -> str | None:
    """Generate a dedicated BTC market update with verified-news-backed guidance."""
    btc_price = None
    if prices:
        btc_price = prices.get("BTC/USD")

    price_ctx = ""
    if btc_price:
        price_ctx = f"Bitcoin is currently at ${btc_price:,.2f}."

    news_context = ""
    try:
        import main
        articles = main.fetch_latest_articles("Bitcoin crypto ETF regulation")
        btc_news = []
        for article in articles[:8]:
            title = (article.get("title") or article.get("headline") or "").strip()
            if title:
                text = f"{title} {article.get('description') or ''}".lower()
                if any(k in text for k in ["bitcoin", "btc", "crypto", "etf", "regulation", "inflation", "fed"]):
                    btc_news.append(article)
            if len(btc_news) >= 3:
                break
        news_context = _extract_news_context(btc_news)
    except Exception:
        news_context = ""

    prompt = (
        "You are a crypto market analyst. Generate a Bitcoin market update that is grounded in recent verified BTC/crypto news rather than generic hype.\n\n"
        f"{price_ctx}\n\n"
        f"{news_context}\n\n"
        "Structure your response EXACTLY like this:\n"
        "SIGNAL|<direction (BULLISH/BEARISH/NEUTRAL)>\n"
        "ANALYSIS|<1-2 sentences on market conditions with evidence from recent news>\n"
        "KEY_LEVEL|<key price level to watch>\n"
        "NEWS|<3 short bullet-style points that mention concrete recent news cues>\n"
        "TRADE|<one-sentence trade setup with entry/target/risk logic>\n"
        "RISK|<one sentence on risk management>\n\n"
        "Be factual, evidence-based, and concise."
    )
    return _best_ai(prompt, "You are a professional crypto market analyst.")


def build_premium_btc_card(signal: str, price: float | None, news_items: list[str], trade_setup: str, risk_note: str) -> str:
    """Build a premium-looking BTC Telegram card for live broadcasts."""
    headline_block = "\n".join(f"• {item[:110]}" for item in news_items[:3]) if news_items else "• No fresh BTC headlines detected"
    price_line = f"${price:,.2f}" if price is not None else "Live"
    return "\n".join([
        "₿ BTC/USD — News-Backed BTC Trade Insight",
        "━━━━━━━━━━━━━━━━━━",
        f"🟢 Signal: {signal}",
        f"💰 Price: {price_line}",
        "",
        "🎯 Trade Setup",
        trade_setup or "Monitor structure and wait for confirmation.",
        "",
        "🛡️ Risk Control",
        risk_note or "Risk 1-2% and scale only after confirmation.",
        "",
        "📰 Verified news",
        headline_block,
        "",
        "⚠️ Not financial advice. Trade at your own risk.",
    ])


def merge_news_streams(feed_items: list[dict], twitter_items: list[dict]) -> list[str]:
    """Merge feed and Twitter headlines while deduplicating similar entries."""
    seen: set[str] = set()
    merged: list[str] = []
    for item in feed_items + twitter_items:
        text = (item.get("title") or item.get("text") or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(text)
    return merged[:5]


def format_btc_market_update(ai_output: str, btc_price: float | None = None) -> str | None:
    """Format BTC market update into a Telegram message with a news-backed structure."""
    if not ai_output:
        return None

    lines = ai_output.strip().split("\n")
    signal = ""
    analysis = ""
    key_level = ""
    news_items: list[str] = []
    trade_setup = ""
    risk_note = ""

    for line in lines:
        line = line.strip()
        if line.upper().startswith("SIGNAL|"):
            signal = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("ANALYSIS|"):
            analysis = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("KEY_LEVEL|"):
            key_level = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("NEWS|"):
            raw = line.split("|", 1)[-1].strip()
            if raw:
                parts = []
                for part in raw.replace("•", "\n").splitlines():
                    cleaned = part.strip(" •-")
                    if cleaned:
                        parts.append(cleaned)
                news_items.extend(parts)
        elif line.upper().startswith("TRADE|"):
            trade_setup = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("RISK|"):
            risk_note = line.split("|", 1)[-1].strip()

    if not signal and not analysis:
        return None

    if trade_setup or risk_note or news_items:
        return build_premium_btc_card(
            signal=signal or "Neutral",
            price=btc_price,
            news_items=news_items,
            trade_setup=trade_setup or f"Key level: {key_level or 'monitor'}",
            risk_note=risk_note or "Risk 1-2% and scale only after confirmation.",
        )

    signal_icon = {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡",
    }.get(signal.upper(), "🟡")

    price_line = ""
    if btc_price:
        price_line = f"💰 *Price:* ${btc_price:,.2f}"

    parts = [
        "₿ *BTC/USD — News-Backed BTC Trade Insight*",
        "━━━━━━━━━━━━━━━━━━",
    ]
    if signal:
        parts.append(f"{signal_icon} *Signal:* {signal}")
    if price_line:
        parts.append(price_line)
    if analysis:
        parts.append(f"\n📊 *Analysis:* {analysis}")
    if key_level:
        parts.append(f"🎯 *Key Level:* {key_level}")
    if trade_setup:
        parts.append(f"\n🎯 *Trade Setup:* {trade_setup}")
    if risk_note:
        parts.append(f"🛡️ *Risk:* {risk_note}")
    if news_items:
        parts.append("\n📰 *Verified news:*")
        for item in news_items[:3]:
            parts.append(f"• {item}")

    parts.extend([
        "",
        "🔖 #BTC  #crypto  #Bitcoin  #newsbacked",
        "⚠️ _Not financial advice. Trade at your own risk._",
    ])
    return "\n".join(parts)


def build_premium_asset_card(asset: str, signal: str, price: float | None, news_items: list[str], trade_setup: str, risk_note: str) -> str:
    """Build a premium-looking asset Telegram card for live broadcasts."""
    headline_block = "\n".join(f"• {item[:110]}" for item in news_items[:3]) if news_items else f"• No fresh {asset} headlines detected"
    
    if "INR" in asset or asset in ["NIFTY", "SENSEX", "RELIANCE", "TCS", "HDFC"]:
        price_str = f"₹{price:,.2f}" if price is not None else "Live"
    elif asset in ["XAU/USD", "EUR/USD", "GBP/USD", "BTC/USD", "ETH/USD", "US100"]:
        price_str = f"${price:,.4f}" if price is not None and price < 5 else (f"${price:,.2f}" if price is not None else "Live")
    else:
        price_str = f"{price}" if price is not None else "Live"

    asset_display = {
        "BTC/USD": "₿ BTC/USD — News-Backed BTC Trade Insight",
        "XAU/USD": "🏆 Gold (XAU/USD) — Macro Strategy Insight",
        "EUR/USD": "💶 EUR/USD — Forex Market Insight",
        "US100": "📈 NASDAQ (US100) — Tech Market Insight",
    }.get(asset, f"📊 {asset} — Market Insight")

    return "\n".join([
        asset_display,
        "━━━━━━━━━━━━━━━━━━",
        f"🟢 Signal: {signal}",
        f"💰 Price: {price_str}",
        "",
        "🎯 Trade Setup",
        trade_setup or "Monitor structure and wait for confirmation.",
        "",
        "🛡️ Risk Control",
        risk_note or "Risk 1-2% and scale only after confirmation.",
        "",
        "📰 Verified news",
        headline_block,
        "",
        "⚠️ Not financial advice. Trade at your own risk.",
    ])


def generate_asset_market_update(asset: str, prices: dict | None = None) -> str | None:
    """Generate a dedicated market update for a specific asset with news-backed guidance."""
    asset_query_map = {
        "BTC/USD": ("Bitcoin crypto ETF regulation", "crypto market analyst"),
        "XAU/USD": ("Gold commodity inflation fed interest rates", "precious metals strategy analyst"),
        "EUR/USD": ("EURUSD forex ECB Fed interest rates economic data", "forex currency analyst"),
        "US100": ("Nasdaq tech stocks inflation fed corporate earnings", "stock index strategy analyst")
    }
    query, analyst_role = asset_query_map.get(asset, (f"{asset} financial news", "market analyst"))

    price = None
    if prices:
        price = prices.get(asset)
    elif asset == "BTC/USD":
        try:
            import main
            price = main.fetch_current_prices().get("BTC/USD")
        except Exception:
            pass

    price_ctx = ""
    if price:
        price_ctx = f"{asset} is currently at {price}."

    news_context = ""
    try:
        import main
        articles = main.fetch_latest_articles(query)
        asset_news = []
        keywords = asset.lower().split("/") + query.lower().split()
        for article in articles[:8]:
            title = (article.get("title") or article.get("headline") or "").strip()
            if title:
                text = f"{title} {article.get('description') or ''}".lower()
                if any(k in text for k in keywords):
                    asset_news.append(article)
            if len(asset_news) >= 3:
                break
        if not asset_news and articles:
            asset_news = articles[:3]
        news_context = _extract_news_context(asset_news)
    except Exception:
        news_context = ""

    prompt = (
        f"You are a professional {analyst_role}. Generate a {asset} market update that is grounded in recent verified news rather than generic hype.\n\n"
        f"{price_ctx}\n\n"
        f"{news_context}\n\n"
        "Structure your response EXACTLY like this:\n"
        "SIGNAL|<direction (BULLISH/BEARISH/NEUTRAL)>\n"
        "ANALYSIS|<1-2 sentences on market conditions with evidence from recent news>\n"
        "KEY_LEVEL|<key price level to watch>\n"
        "NEWS|<3 short bullet-style points that mention concrete recent news cues>\n"
        "TRADE|<one-sentence trade setup with entry/target/risk logic>\n"
        "RISK|<one sentence on risk management>\n\n"
        "Be factual, evidence-based, and concise."
    )
    return _best_ai(prompt, f"You are a professional {analyst_role}.")


def format_asset_market_update(asset: str, ai_output: str, price: float | None = None) -> str | None:
    """Format asset market update into a Telegram message with a news-backed structure."""
    if not ai_output:
        return None

    lines = ai_output.strip().split("\n")
    signal = ""
    analysis = ""
    key_level = ""
    news_items: list[str] = []
    trade_setup = ""
    risk_note = ""

    for line in lines:
        line = line.strip()
        if line.upper().startswith("SIGNAL|"):
            signal = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("ANALYSIS|"):
            analysis = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("KEY_LEVEL|"):
            key_level = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("NEWS|"):
            raw = line.split("|", 1)[-1].strip()
            if raw:
                parts = []
                for part in raw.replace("•", "\n").splitlines():
                    cleaned = part.strip(" •-")
                    if cleaned:
                        parts.append(cleaned)
                news_items.extend(parts)
        elif line.upper().startswith("TRADE|"):
            trade_setup = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("RISK|"):
            risk_note = line.split("|", 1)[-1].strip()

    if not signal and not analysis:
        return None

    return build_premium_asset_card(
        asset=asset,
        signal=signal or "Neutral",
        price=price,
        news_items=news_items,
        trade_setup=trade_setup or f"Key level: {key_level or 'monitor'}",
        risk_note=risk_note or "Risk 1-2% and scale only after confirmation.",
    )


def generate_calendar_trade_setup(event: dict) -> str | None:
    """Generate a high-probability trade setup scenario matrix based on upcoming calendar release forecast and previous metrics."""
    title = event.get("title", "")
    country = event.get("country", "").upper()
    forecast = event.get("forecast", "N/A")
    previous = event.get("previous", "N/A")
    
    pairs_map = {
        "USD": "EUR/USD",
        "EUR": "EUR/USD",
        "GBP": "GBP/USD",
        "JPY": "USD/JPY",
        "AUD": "AUD/USD",
        "CAD": "USD/CAD",
        "CHF": "USD/CHF",
        "NZD": "NZD/USD",
        "INR": "USD/INR",
    }
    pair = pairs_map.get(country, "EUR/USD")
    
    prompt = (
        f"You are a professional macroeconomic strategist. Provide a pre-release scenario matrix and high-probability trade setups for {pair} based on this upcoming news event:\n"
        f"Event: {title} ({country})\n"
        f"Forecast: {forecast} | Previous: {previous}\n\n"
        f"Draft a clear trade setup for two outcomes:\n"
        f"1. Better-Than-Expected Release: Direction (BUY/SELL) for {pair}, suggested Entry/TP/SL, and 1-sentence logic.\n"
        f"2. Worse-Than-Expected Release: Direction (BUY/SELL) for {pair}, suggested Entry/TP/SL, and 1-sentence logic.\n\n"
        "Structure the output exactly like this:\n"
        "EVENT| <event title>\n"
        "SCENARIO_BETTER| Direction: <BUY/SELL> | Entry: <price> | TP: <price> | SL: <price> | Logic: <reasoning>\n"
        "SCENARIO_WORSE| Direction: <BUY/SELL> | Entry: <price> | TP: <price> | SL: <price> | Logic: <reasoning>\n"
        "RISK| <1 sentence risk management note>"
    )
    
    ai_out = _best_ai(prompt, "You are a professional macroeconomic strategy analyst.")
    if not ai_out:
        return None
        
    lines = ai_out.strip().split("\n")
    s_better = s_worse = r_note = ""
    for line in lines:
        line = line.strip()
        if line.upper().startswith("SCENARIO_BETTER|"):
            s_better = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("SCENARIO_WORSE|"):
            s_worse = line.split("|", 1)[-1].strip()
        elif line.upper().startswith("RISK|"):
            r_note = line.split("|", 1)[-1].strip()
            
    if not s_better and not s_worse:
        return None
        
    return "\n".join([
        f"📅 *HIGH IMPACT EVENT SIGNALS*",
        f"━━━━━━━━━━━━━━━━━━",
        f"📢 *Event:* {title} ({country})",
        f"📊 *Forecast:* {forecast}  ·  *Previous:* {previous}",
        f"💿 *Trade Pair:* {pair}",
        f"",
        f"🟢 *Scenario 1 (Better Outcome):*",
        s_better or "Monitor release and trade directionally.",
        f"",
        f"🔴 *Scenario 2 (Worse Outcome):*",
        s_worse or "Monitor release and trade directionally.",
        f"",
        f"🛡️ *Risk Note:* {r_note or 'Keep leverage low before release volatility.'}",
        f"━━━━━━━━━━━━━━━━━━",
        f"🔖 #forexfactory #macro #{country} #{pair.replace('/', '')}",
    ])


if __name__ == "__main__":
    print("AI Agent module loaded. Used by main.py for message enhancement.")
