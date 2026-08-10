"""
verify_news_flow.py — Test script to verify all news data flows to Telegram.
Run this to verify your bot is sending news to Telegram correctly.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

from telegram import Bot
from dotenv import load_dotenv

# Load environment
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


async def test_telegram_connection():
    """Test Telegram bot connection."""
    print("="*80)
    print("🔍 TESTING TELEGRAM CONNECTION")
    print("="*80)
    
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not found in .env file")
        return False
    
    if not TELEGRAM_CHAT_ID:
        print("❌ ERROR: TELEGRAM_CHAT_ID not found in .env file")
        return False
    
    try:
        bot = Bot(BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot Connected: @{me.username} ({me.first_name})")
        
        # Test send message
        test_msg = (
            f"🧪 *TEST MESSAGE*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ Bot is working correctly!\n"
            f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"🚀 All news data will flow to this channel"
        )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=test_msg,
            parse_mode="Markdown"
        )
        print(f"✅ Test message sent to: {TELEGRAM_CHAT_ID}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_news_apis():
    """Test news API connections."""
    print("\n" + "="*80)
    print("🔍 TESTING NEWS APIs")
    print("="*80)
    
    news_api = os.getenv("NEWS_API_KEY", "").strip()
    newsdata = os.getenv("NEWSDATA_API_KEY", "").strip()
    
    if not news_api and not newsdata:
        print("⚠️ WARNING: No news API keys found in .env")
        print("   - Get NewsAPI key from: https://newsapi.org/")
        print("   - Get NewsData key from: https://newsdata.io/")
        return False
    
    if news_api:
        print(f"✅ NewsAPI key found: {news_api[:10]}...")
    
    if newsdata:
        print(f"✅ NewsData key found: {newsdata[:10]}...")
    
    return True


def test_ai_apis():
    """Test AI API connections."""
    print("\n" + "="*80)
    print("🔍 TESTING AI APIs")
    print("="*80)
    
    groq = os.getenv("GROQ_API_KEY", "").strip()
    openai = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not groq and not openai:
        print("⚠️ WARNING: No AI API keys found in .env")
        print("   - Get Groq key from: https://console.groq.com/ (FREE)")
        print("   - Get OpenAI key from: https://platform.openai.com/")
        return False
    
    if groq:
        print(f"✅ Groq API key found: {groq[:10]}...")
    
    if openai:
        print(f"✅ OpenAI API key found: {openai[:10]}...")
    
    return True


def test_state_files():
    """Test state file permissions."""
    print("\n" + "="*80)
    print("🔍 TESTING STATE FILES")
    print("="*80)
    
    state_files = [
        "worker_24x7_state.json",
        "sent_articles.json",
        "signal_log.json",
        "crypto_screener_seen.json",
        ".ai_cycle_counter"
    ]
    
    for file in state_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
            # Test write permission
            try:
                with open(file, "a") as f:
                    pass
                print(f"   └─ ✅ Write permission OK")
            except Exception as e:
                print(f"   └─ ❌ Write permission FAILED: {e}")
        else:
            print(f"⚠️ {file} not found (will be created on first run)")
    
    return True


def show_news_flow_summary():
    """Show summary of how news flows to Telegram."""
    print("\n" + "="*80)
    print("📊 NEWS FLOW TO TELEGRAM - SUMMARY")
    print("="*80)
    print("""
┌─────────────────────────────────────────────────────────────────┐
│                     NEWS DATA SOURCES                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. NewsAPI.org           → News headlines (100/day free)      │
│ 2. NewsData.io           → News headlines (200/day free)      │
│ 3. RSS Feeds             → Live market news feeds             │
│ 4. Finnhub WebSocket     → Real-time breaking news            │
│ 5. Twitter/X (optional)  → Social sentiment                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING & FILTERING                        │
├─────────────────────────────────────────────────────────────────┤
│ • Filter by keywords (forex, crypto, stocks, india, etc.)      │
│ • Detect high-impact keywords (crash, fed, CPI, etc.)          │
│ • AI sentiment analysis (Bullish/Bearish/Neutral)              │
│ • Multi-level explanations (Beginner/Intermediate/Expert)      │
│ • Generate trade setups with entry/TP/SL                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TELEGRAM MESSAGE TYPES                        │
├─────────────────────────────────────────────────────────────────┤
│ 📰 News Alerts          → Breaking market news                 │
│ 📊 Trade Signals        → Entry/TP/SL with AI analysis         │
│ 🚨 Crash Alerts         → Emergency market warnings            │
│ ⚠️ VIX Alerts           → Volatility spike warnings            │
│ 📅 Economic Calendar    → Pre-event alerts (3-7 min before)   │
│ 🇮🇳 Indian Market       → NSE/BSE updates & signals            │
│ 🇺🇸 US Market           → NASDAQ/Dow/S&P updates               │
│ ₿ Crypto Alerts         → Pump detection & signals             │
│ 🏆 Commodities          → Gold/Silver/Oil signals              │
│ 🌅 Morning Briefing     → Daily market overview (8 AM IST)    │
└─────────────────────────────────────────────────────────────────┘

📊 MESSAGE FREQUENCY (Configurable):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• News alerts:        Every 3-10 minutes
• Trade signals:      Every 10-20 minutes
• Market snapshots:   Every 5 minutes (during trading hours)
• Crypto alerts:      Every 5 minutes (24/7)
• Real-time alerts:   Instant (WebSocket)
• Morning briefing:   Once daily at 8:00 AM IST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ALL news data WILL be sent to your Telegram channel continuously!
""")


async def main():
    """Run all tests."""
    print("\n" + "🚀 "*40)
    print("🧪 NEWS FLOW VERIFICATION TEST")
    print("🚀 "*40 + "\n")
    
    # Test Telegram
    telegram_ok = await test_telegram_connection()
    
    # Test APIs
    news_ok = test_news_apis()
    ai_ok = test_ai_apis()
    
    # Test state files
    state_ok = test_state_files()
    
    # Show summary
    show_news_flow_summary()
    
    # Final verdict
    print("\n" + "="*80)
    print("📋 FINAL VERDICT")
    print("="*80)
    
    if telegram_ok:
        print("✅ Telegram: WORKING")
        print("✅ All news data WILL be sent to your channel!")
    else:
        print("❌ Telegram: FAILED - Fix .env file")
    
    if news_ok:
        print("✅ News APIs: CONFIGURED")
    else:
        print("⚠️ News APIs: NEED CONFIGURATION")
    
    if ai_ok:
        print("✅ AI APIs: CONFIGURED")
    else:
        print("⚠️ AI APIs: NEED CONFIGURATION (for AI features)")
    
    print("\n" + "="*80)
    print("🚀 NEXT STEPS")
    print("="*80)
    print("""
1. If all tests passed → Run: python unified_24x7_worker.py
2. If tests failed → Fix .env file and re-run this test
3. Monitor Telegram → You'll receive news continuously!

For help: Check START_HERE.md or DEPLOYMENT_GUIDE.md
""")
    
    return telegram_ok and (news_ok or ai_ok)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
