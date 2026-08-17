"""
unified_24x7_worker.py — Comprehensive 24/7 Market Monitoring Bot
=====================================================================
Monitors ALL markets continuously and sends Telegram messages based on:
- Market hours and sessions (Asian, European, US)
- Real-time price movements and alerts
- Economic calendar events
- News and sentiment analysis
- Technical signals across ALL asset classes

Markets Covered 24/7:
- Indian Equity (NSE/BSE): Nifty, Sensex, Bank Nifty, Indian stocks
- US Markets: NASDAQ, Dow Jones, S&P 500, US stocks
- Forex: Major pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- Commodities: Gold (XAU/USD), Silver, Crude Oil, Brent
- Crypto: Bitcoin, Ethereum, Solana, XRP, Cardano, Dogecoin, etc.
- Cash Market: Real-time intraday signals

Architecture:
- Multiple parallel monitoring threads for each market
- WebSocket connections for real-time data
- Smart scheduling based on market hours
- Rate limiting to avoid Telegram spam
- Persistent state across restarts
"""

import asyncio
import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from telegram import Bot
from telegram.error import TelegramError

# Import existing modules
import ai_agent
import crypto_screener
import indian_market
import main
import realtime_alert
from main import (
    BOT_TOKEN,
    BOT_TOKEN2,
    BOT_TOKEN3,
    TELEGRAM_CHAT_ID,
    TELEGRAM_CHAT_ID3,
    fetch_current_prices,
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

CHECK_INTERVAL_FAST = 30      # 30 seconds for active market hours
CHECK_INTERVAL_SLOW = 120     # 2 minutes for off-peak hours
NEWS_CHECK_INTERVAL = 180     # 3 minutes for news
CRYPTO_CHECK_INTERVAL = 300   # 5 minutes for crypto screening
INDIAN_MARKET_INTERVAL = 60   # 1 minute during Indian market hours
US_MARKET_INTERVAL = 60       # 1 minute during US market hours
FOREX_SIGNAL_INTERVAL = 600   # 10 minutes for forex signals

STATE_FILE = "worker_24x7_state.json"
MESSAGE_COOLDOWN = 120        # 2 minutes between similar messages

# ═══════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

class WorkerState:
    """Manages persistent state for 24/7 worker."""
    
    def __init__(self):
        self.last_message_times: dict[str, float] = {}
        self.daily_message_count: dict[str, int] = {}
        self.last_reset_day = datetime.now(timezone.utc).date().isoformat()
        self.load()
    
    def load(self):
        """Load state from disk."""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE) as f:
                    data = json.load(f)
                    self.last_message_times = data.get("last_message_times", {})
                    self.daily_message_count = data.get("daily_message_count", {})
                    self.last_reset_day = data.get("last_reset_day", self.last_reset_day)
        except Exception as e:
            print(f"[STATE] Load error: {e}")
    
    def save(self):
        """Save state to disk."""
        try:
            with open(STATE_FILE, "w") as f:
                json.dump({
                    "last_message_times": self.last_message_times,
                    "daily_message_count": self.daily_message_count,
                    "last_reset_day": self.last_reset_day,
                }, f)
        except Exception as e:
            print(f"[STATE] Save error: {e}")
    
    def can_send_message(self, category: str, cooldown: int = MESSAGE_COOLDOWN) -> bool:
        """Check if enough time has passed since last message in this category."""
        now = time.time()
        last_time = self.last_message_times.get(category, 0)
        
        # Reset daily counter if new day
        current_day = datetime.now(timezone.utc).date().isoformat()
        if current_day != self.last_reset_day:
            self.daily_message_count = {}
            self.last_reset_day = current_day
            self.save()
        
        return (now - last_time) >= cooldown
    
    def record_message(self, category: str):
        """Record that a message was sent."""
        now = time.time()
        self.last_message_times[category] = now
        self.daily_message_count[category] = self.daily_message_count.get(category, 0) + 1
        self.save()


state = WorkerState()

# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM BROADCASTING
# ═══════════════════════════════════════════════════════════════════════════

async def broadcast_message(bot: Bot, text: str, parse_mode: str = "Markdown") -> bool:
    """Broadcast message to all configured Telegram channels."""
    success = False
    
    # Primary bot
    if BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            success = True
        except TelegramError as e:
            print(f"[TELEGRAM] Primary bot error: {e}")
    
    # Secondary bot (if configured)
    if BOT_TOKEN2 and TELEGRAM_CHAT_ID:
        try:
            bot2 = Bot(BOT_TOKEN2)
            await bot2.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
        except TelegramError as e:
            print(f"[TELEGRAM] Secondary bot error: {e}")
    
    # Tertiary bot (if configured)
    if BOT_TOKEN3 and (TELEGRAM_CHAT_ID3 or TELEGRAM_CHAT_ID):
        try:
            bot3 = Bot(BOT_TOKEN3)
            chat_id = TELEGRAM_CHAT_ID3 or TELEGRAM_CHAT_ID
            await bot3.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
        except TelegramError as e:
            print(f"[TELEGRAM] Tertiary bot error: {e}")
    
    return success


# ═══════════════════════════════════════════════════════════════════════════
# MARKET HOURS DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_current_market_session() -> dict[str, bool]:
    """Determine which markets are currently open."""
    now_utc = datetime.now(timezone.utc)
    hour_utc = now_utc.hour
    weekday = now_utc.weekday()  # 0=Monday, 6=Sunday
    
    # Indian market: 9:15 AM - 3:30 PM IST = 3:45 AM - 10:00 AM UTC (Mon-Fri)
    ist_now = now_utc + timedelta(hours=5, minutes=30)
    indian_open = (
        weekday < 5 and  # Mon-Fri
        9 <= ist_now.hour < 15 or (ist_now.hour == 15 and ist_now.minute <= 30)
    )
    
    # US market: 9:30 AM - 4:00 PM EST/EDT = ~14:30 - 21:00 UTC (Mon-Fri)
    us_open = weekday < 5 and 14 <= hour_utc < 21
    
    # European market: 8:00 AM - 4:30 PM GMT = 8:00 - 16:30 UTC (Mon-Fri)
    europe_open = weekday < 5 and 8 <= hour_utc < 17
    
    # Asian market: 9:00 AM - 3:00 PM JST = 0:00 - 6:00 UTC (Mon-Fri)
    asian_open = weekday < 5 and 0 <= hour_utc < 6
    
    # Forex: 24/5 (closes Fri 10PM UTC, opens Sun 10PM UTC)
    forex_open = not (weekday == 5 or (weekday == 6 and hour_utc < 22))
    
    # Crypto: 24/7
    crypto_open = True
    
    return {
        "indian": indian_open,
        "us": us_open,
        "europe": europe_open,
        "asian": asian_open,
        "forex": forex_open,
        "crypto": crypto_open,
    }


# ═══════════════════════════════════════════════════════════════════════════
# MARKET-SPECIFIC MONITORS
# ═══════════════════════════════════════════════════════════════════════════

async def monitor_indian_market(bot: Bot):
    """Monitor Indian equity market during trading hours."""
    category = "indian_market"
    
    while True:
        try:
            sessions = get_current_market_session()
            
            # Pre-Market Options Breakout Report (at 9:00 - 9:15 AM IST)
            ist_now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
            if ist_now.weekday() < 5 and ist_now.hour == 9 and 0 <= ist_now.minute <= 15:
                if state.can_send_message("indian_premarket_breakout", 80000): # at most once a day
                    try:
                        print("[INDIAN] Running pre-market options breakout scan...")
                        import indian_scoring as iscoring
                        candidates = iscoring.scan_breakout_candidates(exchange="NSE")
                        
                        # Find the top candidate that has a breakout status
                        breakout_c = None
                        for c in candidates:
                            if c.get("status") in ("PUMP BREAKOUT", "DUMP BREAKOUT") and c.get("option_contract") != "—":
                                breakout_c = c
                                break
                        
                        # If no breakout, pick the one with the tightest consolidation range as a pre-market watch
                        if not breakout_c and candidates:
                            candidates_sorted = sorted(candidates, key=lambda x: x.get("range_pct", 99.0))
                            breakout_c = candidates_sorted[0]
                            
                        if breakout_c:
                            ticker = breakout_c["ticker"]
                            status = breakout_c["status"]
                            option_contract = breakout_c["option_contract"]
                            option_premium = breakout_c["option_premium"]
                            spot = breakout_c["price"]
                            range_pct = breakout_c["range_pct"]
                            volume_ratio = breakout_c["volume_ratio"]
                            sector = breakout_c["sector"]
                            
                            # Analyze breakout using AI
                            prompt = (
                                f"Analyze this intraday breakout stock setup:\n"
                                f"Stock Ticker: {ticker} (NSE)\n"
                                f"Breakout Status: {status}\n"
                                f"Most Liquid Option Contract: {option_contract}\n"
                                f"Option Last Premium Price: ₹{option_premium}\n\n"
                                f"Generate a professional options trade recommendation. Output strictly a JSON object with these exact keys:\n"
                                f"- 'action': e.g. 'BUY CALL', 'BUY PUT'\n"
                                f"- 'strike_target': option contract name, e.g. '{option_contract}'\n"
                                f"- 'premium_entry': option premium entry price, e.g. {option_premium}\n"
                                f"- 'sl': stop loss premium price\n"
                                f"- 'tp1': target 1 premium price (must represent exactly a 1:5 Risk-to-Reward ratio relative to entry and Stop Loss)\n"
                                f"- 'tp2': target 2 premium price (must represent exactly a 1:10 Risk-to-Reward ratio relative to entry and Stop Loss)\n"
                                f"- 'rationale': 2-sentence rationale detailing why the breakout from the 3-day consolidation pattern supports this trade.\n"
                            )
                            
                            raw_res = main._analyzer_groq_chat(prompt, system_prompt="You are an elite quantitative derivatives analyst. Respond ONLY with valid JSON.", json_mode=True)
                            import re
                            match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                            if match:
                                ai_trade = json.loads(match.group())
                                action = ai_trade.get("action", "BUY CALL")
                                entry = ai_trade.get("premium_entry", option_premium)
                                sl = ai_trade.get("sl", "0.0")
                                tp1 = ai_trade.get("tp1", "0.0")
                                tp2 = ai_trade.get("tp2", "0.0")
                                rationale = ai_trade.get("rationale", "")
                                
                                telegram_msg = (
                                    f"🇮🇳 <b>PRE-MARKET F&O BREAKOUT OPTIONS ALERT</b>\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📊 <b>Breakout Stock:</b> <b>{ticker}</b> ({sector})\n"
                                    f"📈 Spot Price: <b>₹{spot:,.2f}</b>\n"
                                    f"📉 3-Day Consolidation Range: <b>{range_pct}%</b>\n"
                                    f"🔊 Volume Volatility: <b>{volume_ratio}x</b>\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🎯 <b>Option Trade Recommendation</b>\n"
                                    f"🔹 Action: <b>{action}</b>\n"
                                    f"🔸 Option Contract: <b>{option_contract}</b>\n"
                                    f"🔹 Entry Premium: <b>₹{entry}</b>\n"
                                    f"🔸 Stop Loss: <b>₹{sl}</b>\n"
                                    f"🔹 Target 1 (1:5 R:R): <b>₹{tp1}</b>\n"
                                    f"🔸 Target 2 (1:10 R:R): <b>₹{tp2}</b>\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📝 <b>Trade Rationale:</b> {rationale}\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🤖 <i>Powered by Breakout Options Agent</i>"
                                )
                                await broadcast_message(bot, telegram_msg, parse_mode="HTML")
                                state.record_message("indian_premarket_breakout")
                                print(f"[INDIAN] Daily pre-market options breakout alert broadcasted for {ticker}")
                    except Exception as pre_err:
                        print(f"[INDIAN] Pre-market options alert broadcast failed: {pre_err}")

            # Market Open Intraday Options Flags & OI Build Report (at 9:15 - 9:30 AM IST)
            if ist_now.weekday() < 5 and ist_now.hour == 9 and 15 <= ist_now.minute <= 30:
                if state.can_send_message("indian_market_open_flags", 80000): # at most once a day
                    try:
                        print("[INDIAN] Running Market Open options flag scan...")
                        import indian_scoring as iscoring
                        intel = iscoring.get_full_intel(exchange="NSE")
                        campaigns = intel.get("campaigns", [])
                        
                        flag_lines = []
                        for c in campaigns[:5]:
                            legs_str = " | ".join([f"{l['name']} {l['amount']}" for l in c.get('legs', [])])
                            warn_str = f"\n  ⚠️ <i>{c['warning']}</i>" if c.get('warning') else ""
                            flag_lines.append(
                                f"• <b>{c['ticker']}</b> [{c['status_flag']}] ({c['direction']})\n"
                                f"  💰 Gross Flow: <b>{c['gross_flow']}</b> ({c['net_flow']})\n"
                                f"  📈 OI Build: <b>{c['oi_build']}</b>\n"
                                f"  🧩 Legs: {legs_str}{warn_str}"
                            )
                        flag_text = "\n\n".join(flag_lines) if flag_lines else "No active flags at open."
                        
                        pcr_watch = intel.get("pcr_watch", [])
                        pcr_str = " | ".join([f"{p['index']}: <b>{p['pcr']}</b>" for p in pcr_watch[:3]])
                        
                        date_str = ist_now.strftime("%d %b %Y")
                        telegram_open_msg = (
                            f"🇮🇳 <b>INDIAN MARKET OPEN: INTRADAY OPTIONS FLAGS ({date_str})</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🛡 <b>GRADED INSTITUTIONAL STRIKE FLAGS</b>\n\n"
                            f"{flag_text}\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📊 <b>OPENING INDEX PCR</b>\n"
                            f"{pcr_str}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🤖 <i>Powered by Options Flow Engine</i>"
                        )
                        await broadcast_message(bot, telegram_open_msg, parse_mode="HTML")
                        state.record_message("indian_market_open_flags")
                        print("[INDIAN] Market Open intraday options flags broadcasted to Telegram")
                    except Exception as open_err:
                        print(f"[INDIAN] Market Open options flags broadcast failed: {open_err}")

            if sessions["indian"] and state.can_send_message(category, 300):  # 5 min cooldown
                # Fetch Indian market snapshot
                snapshot = indian_market.format_market_snapshot()
                if snapshot:
                    message = f"🇮🇳 *Indian Market Update*\n{snapshot}"
                    await broadcast_message(bot, message, parse_mode="HTML")
                    state.record_message(category)
                    print(f"[INDIAN] Market snapshot sent")
                
                # Options suggestions (less frequent)
                if state.can_send_message(f"{category}_options", 1800):  # 30 min
                    nifty_opts = indian_market.format_nifty_options_suggestion()
                    if nifty_opts:
                        await broadcast_message(bot, nifty_opts, parse_mode="HTML")
                        state.record_message(f"{category}_options")
                        print(f"[INDIAN] Options suggestion sent")
            
            # Check every minute during market hours, every 5 minutes otherwise
            sleep_time = INDIAN_MARKET_INTERVAL if sessions["indian"] else 300
            await asyncio.sleep(sleep_time)
            
        except Exception as e:
            print(f"[INDIAN] Monitor error: {e}")
            await asyncio.sleep(60)


async def monitor_us_market(bot: Bot):
    """Monitor US stock market during trading hours."""
    category = "us_market"
    
    while True:
        try:
            sessions = get_current_market_session()
            
            if sessions["us"] and state.can_send_message(category, 300):  # 5 min cooldown
                # Fetch US market snapshot
                global_snap = indian_market.format_global_snapshot()
                if global_snap:
                    message = f"🇺🇸 *US Market Update*\n{global_snap}"
                    await broadcast_message(bot, message, parse_mode="HTML")
                    state.record_message(category)
                    print(f"[US] Market snapshot sent")
            
            # Check every minute during market hours, every 5 minutes otherwise
            sleep_time = US_MARKET_INTERVAL if sessions["us"] else 300
            await asyncio.sleep(sleep_time)
            
        except Exception as e:
            print(f"[US] Monitor error: {e}")
            await asyncio.sleep(60)


async def monitor_forex_signals(bot: Bot):
    """Generate and send forex trading signals."""
    category = "forex_signals"
    
    while True:
        try:
            sessions = get_current_market_session()
            
            if sessions["forex"] and state.can_send_message(category, FOREX_SIGNAL_INTERVAL):
                # Run main forex signal generation cycle
                seen_keys = main.load_seen_keys()
                sent = await main.run_worker_cycle(bot, seen_keys)
                main.save_seen_keys(seen_keys)
                
                if sent > 0:
                    state.record_message(category)
                    print(f"[FOREX] Sent {sent} signals")
            
            await asyncio.sleep(CHECK_INTERVAL_FAST if sessions["forex"] else CHECK_INTERVAL_SLOW)
            
        except Exception as e:
            print(f"[FOREX] Monitor error: {e}")
            await asyncio.sleep(60)


async def monitor_crypto_market(bot: Bot):
    """Monitor cryptocurrency market 24/7."""
    category = "crypto"
    
    while True:
        try:
            if state.can_send_message(category, CRYPTO_CHECK_INTERVAL):
                # Run crypto screener for pump detection
                sent = crypto_screener.run_scan_cycle()
                
                if sent > 0:
                    state.record_message(category)
                    print(f"[CRYPTO] Sent {sent} pump alerts")
            
            await asyncio.sleep(CRYPTO_CHECK_INTERVAL)
            
        except Exception as e:
            print(f"[CRYPTO] Monitor error: {e}")
            await asyncio.sleep(60)


async def monitor_commodities(bot: Bot):
    """Monitor commodities: Gold, Silver, Crude Oil."""
    category = "commodities"
    
    while True:
        try:
            sessions = get_current_market_session()
            
            if state.can_send_message(category, 600):  # 10 min cooldown
                prices = fetch_current_prices()
                
                # Generate signals for key commodities
                for asset in ["XAU/USD", "XAG/USD", "WTI"]:
                    if asset in prices and state.can_send_message(f"{category}_{asset}", 1800):
                        # Generate AI analysis
                        update = ai_agent.generate_asset_market_update(asset, prices)
                        if update:
                            message = ai_agent.format_asset_market_update(asset, update, prices.get(asset))
                            if message:
                                await broadcast_message(bot, message)
                                state.record_message(f"{category}_{asset}")
                                print(f"[COMMODITIES] {asset} signal sent")
                                await asyncio.sleep(5)  # Small delay between assets
            
            await asyncio.sleep(CHECK_INTERVAL_SLOW)
            
        except Exception as e:
            print(f"[COMMODITIES] Monitor error: {e}")
            await asyncio.sleep(60)


async def monitor_realtime_alerts(bot: Bot):
    """Monitor real-time market alerts (VIX spikes, crashes, etc.)."""
    category = "realtime_alerts"
    
    while True:
        try:
            # Run all polling-based checks
            alert_count = realtime_alert.run_polling_cycle()
            
            if alert_count > 0:
                state.record_message(category)
                print(f"[REALTIME] Sent {alert_count} alerts")
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            print(f"[REALTIME] Monitor error: {e}")
            await asyncio.sleep(60)


async def send_market_briefing(bot: Bot):
    """Send daily morning briefing."""
    category = "morning_briefing"
    
    while True:
        try:
            now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            
            # Send briefing at 8:00 AM IST (before market opens)
            if now_ist.hour == 8 and now_ist.minute < 10:
                if state.can_send_message(category, 82800):  # Once per 23 hours
                    # Generate morning briefing
                    prices = fetch_current_prices()
                    
                    briefing_parts = []
                    briefing_parts.append("🌅 *Good Morning! Market Briefing*")
                    briefing_parts.append("━━━━━━━━━━━━━━━━━━")
                    briefing_parts.append(f"📅 {now_ist.strftime('%A, %B %d, %Y')}")
                    briefing_parts.append("")
                    
                    # Add key market levels
                    briefing_parts.append("📊 *Pre-Market Levels*")
                    for pair in ["NIFTY", "SENSEX", "XAU/USD", "EUR/USD", "BTC/USD"]:
                        p = prices.get(pair)
                        if p:
                            briefing_parts.append(f"  • {pair}: {main._price_str(p, pair)}")
                    
                    briefing_parts.append("")
                    briefing_parts.append("🔖 #morning #briefing #markets")
                    
                    message = "\n".join(briefing_parts)
                    await broadcast_message(bot, message)
                    state.record_message(category)
                    print(f"[BRIEFING] Morning briefing sent")
            
            # Check every 10 minutes
            await asyncio.sleep(600)
            
        except Exception as e:
            print(f"[BRIEFING] Error: {e}")
            await asyncio.sleep(600)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN 24/7 WORKER
# ═══════════════════════════════════════════════════════════════════════════

async def run_24x7_worker():
    """Main 24/7 worker - coordinates all market monitoring tasks."""
    print("="*80)
    print("🚀 Starting 24/7 Comprehensive Market Monitoring Bot")
    print("="*80)
    print(f"📅 Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🌍 Markets: Indian Equity, US Stocks, Forex, Crypto, Commodities")
    print(f"📡 Telegram Channels: {1 + bool(BOT_TOKEN2) + bool(BOT_TOKEN3)}")
    print("="*80)
    
    bot = Bot(BOT_TOKEN)
    
    # Start WebSocket for real-time alerts (runs in separate thread)
    print("[WEBSOCKET] Starting Finnhub WebSocket...")
    ws_thread = realtime_alert.start_websocket_thread()
    
    # Create all monitoring tasks
    tasks = [
        monitor_indian_market(bot),
        monitor_us_market(bot),
        monitor_forex_signals(bot),
        monitor_crypto_market(bot),
        monitor_commodities(bot),
        monitor_realtime_alerts(bot),
        send_market_briefing(bot),
    ]
    
    print(f"[WORKER] Started {len(tasks)} monitoring tasks")
    print("="*80)
    
    # Send startup notification
    startup_msg = (
        "✅ *24/7 Market Bot Online*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Monitoring all markets:\n"
        "🇮🇳 Indian Equity (NSE/BSE)\n"
        "🇺🇸 US Stocks & Indices\n"
        "💱 Forex (All major pairs)\n"
        "₿ Crypto (BTC, ETH, Altcoins)\n"
        "🏆 Commodities (Gold, Silver, Oil)\n"
        "\n"
        "📡 Real-time alerts enabled\n"
        "🤖 AI analysis active\n"
        "🔖 #status #online"
    )
    await broadcast_message(bot, startup_msg)
    
    # Run all tasks concurrently
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n[WORKER] Shutdown requested...")
        shutdown_msg = (
            "⚠️ *24/7 Market Bot Shutting Down*\n"
            "Will restart automatically.\n"
            "🔖 #status #offline"
        )
        await broadcast_message(bot, shutdown_msg)
    except Exception as e:
        print(f"[WORKER] Fatal error: {e}")
        error_msg = (
            "❌ *24/7 Market Bot Error*\n"
            f"Error: {str(e)[:100]}\n"
            "Will attempt restart.\n"
            "🔖 #status #error"
        )
        await broadcast_message(bot, error_msg)
        raise


def main():
    """Entry point for 24/7 worker."""
    asyncio.run(run_24x7_worker())


if __name__ == "__main__":
    main()
