# 🚀 START HERE - Your 24/7 Market Bot

## 📖 What You Have

A **professional 24/7 market monitoring system** that sends real-time Telegram alerts for:

- 🇮🇳 Indian Markets (NSE/BSE, Nifty, Sensex, stocks)
- 🇺🇸 US Markets (NASDAQ, Dow, S&P 500, stocks)
- 💱 Forex (All major currency pairs, 24/5)
- ₿ Crypto (Bitcoin, Ethereum, altcoins, 24/7)
- 🏆 Commodities (Gold, Silver, Crude Oil)

**Features**: Real-time alerts, AI analysis, economic calendar, VIX monitoring, crash detection, pre-market alerts, and more!

---

## ⚡ Quick Start (Choose Your Path)

### 🪟 Windows Users → [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)
**5-minute setup** with double-click startup!

### 🐳 Docker Users (Any OS) → Quick Commands
```bash
# 1. Configure
cp .env.example .env
nano .env  # Add your API keys

# 2. Start
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

### 🐧 Linux/Mac Users → Quick Commands
```bash
# 1. Configure
cp .env.example .env
nano .env  # Add your API keys

# 2. Make script executable
chmod +x start_bot.sh

# 3. Run
./start_bot.sh
```

---

## 🔑 What You Need

### Required API Keys

1. **Telegram Bot**
   - Create: Message [@BotFather](https://t.me/botfather), send `/newbot`
   - Get channel ID: [@userinfobot](https://t.me/userinfobot)
   - Make bot admin in your channel

2. **News API** (Choose one or both)
   - [NewsAPI](https://newsapi.org/) - Free: 100/day
   - [NewsData](https://newsdata.io/) - Free: 200/day

3. **AI API** (Choose one)
   - [Groq](https://console.groq.com/) - **FREE & FAST** ⭐
   - [OpenAI](https://platform.openai.com/) - Paid

### Optional (But Recommended)

4. **Finnhub** (For real-time alerts)
   - [Finnhub.io](https://finnhub.io/) - Free: 60/min

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| **`.env`** | Your API keys (copy from `.env.example`) |
| **`unified_24x7_worker.py`** | Main bot (starts automatically) |
| **`start_bot.bat`** | Windows startup script |
| **`start_bot.sh`** | Linux/Mac startup script |
| **`docker-compose.yml`** | Docker deployment config |

---

## 📚 Full Documentation

| Guide | What It Covers |
|-------|----------------|
| **[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)** | Windows step-by-step (5 min) |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Complete deployment manual |
| **[UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md)** | What's new & why it's better |
| **[README.md](README.md)** | Full project documentation |

---

## ✅ Quick Verification

After starting your bot, you should see in Telegram:

```
✅ 24/7 Market Bot Online
━━━━━━━━━━━━━━━━━━
Monitoring all markets:
🇮🇳 Indian Equity (NSE/BSE)
🇺🇸 US Stocks & Indices
💱 Forex (All major pairs)
₿ Crypto (BTC, ETH, Altcoins)
🏆 Commodities (Gold, Silver, Oil)

📡 Real-time alerts enabled
🤖 AI analysis active
```

**✅ If you see this → You're all set!**

---

## 🐛 Troubleshooting

### No messages in Telegram?
1. Check `.env` file has correct `BOT_TOKEN` and `TELEGRAM_CHAT_ID`
2. Verify bot is admin in channel
3. Check logs for errors
4. Test bot token: Message your bot directly with `/start`

### "Python not found"?
- **Windows**: Reinstall Python with "Add to PATH" checked
- **Linux/Mac**: Install with `sudo apt install python3` or `brew install python3`

### "Module not found" errors?
- Run: `pip install -r requirements.txt`
- Or delete `.venv` folder and restart

### Bot keeps stopping?
- Check API keys are valid
- Ensure stable internet connection
- Review error messages in console/logs
- Use Docker for auto-restart: `docker-compose up -d`

---

## 🎯 What Happens Next

### During Indian Market Hours (9:15 AM - 3:30 PM IST)
- Live Nifty/Sensex updates every 5 minutes
- Top gainers/losers alerts
- Options strategy suggestions every 30 minutes
- Real-time stock signals

### During US Market Hours (9:30 AM - 4:00 PM EST)
- NASDAQ/Dow/S&P 500 updates every 5 minutes
- US stock movers (AAPL, MSFT, GOOGL, etc.)
- Tech sector analysis

### Forex (24/5 Monitoring)
- News-backed signals every 10 minutes
- Economic calendar alerts (3-7 min before events)
- Major currency pair analysis
- USD/INR updates

### Crypto (24/7 Monitoring)
- Pump detection every 5 minutes
- Altcoin reversal signals
- Bitcoin/Ethereum analysis every 2 hours
- Volume surge alerts

### Real-Time Alerts (Always)
- VIX spike warnings
- Crash keyword detection
- Sharp price movement alerts
- Pre-market gap alerts (before NSE opens)

### Daily Routine
- **8:00 AM IST**: Morning market briefing
- **Throughout day**: Real-time signals and news
- **Market close**: End-of-day summary

---

## ⚙️ Customization

### Change Message Frequency

Edit `.env`:

```env
# More messages (for active traders)
MESSAGE_COOLDOWN=60              # 1 min between messages
CHECK_INTERVAL_FAST=15           # Check every 15 seconds

# Fewer messages (for swing traders)
MESSAGE_COOLDOWN=300             # 5 min between messages
CHECK_INTERVAL_FAST=60           # Check every minute
```

### Focus on Specific Markets

In `unified_24x7_worker.py`, comment out monitors you don't need:

```python
tasks = [
    monitor_indian_market(bot),      # ← Keep this
    # monitor_us_market(bot),        # ← Disable this
    monitor_forex_signals(bot),      # ← Keep this
    # monitor_crypto_market(bot),    # ← Disable this
    # monitor_commodities(bot),      # ← Disable this
    monitor_realtime_alerts(bot),    # ← Keep this
]
```

---

## 📞 Need Help?

### Check These First
1. **Logs**: `docker-compose logs -f` or check console window
2. **Configuration**: Verify `.env` file
3. **API Keys**: Test them individually
4. **Documentation**: Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Still Stuck?
- Review [Troubleshooting section](DEPLOYMENT_GUIDE.md#troubleshooting)
- Check [UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md) for limitations
- Open GitHub issue with logs

---

## 🎉 You're Ready!

1. **Choose your path** (Windows, Docker, Linux)
2. **Get API keys** (Telegram, News, AI)
3. **Configure** (`.env` file)
4. **Start** (run script or Docker)
5. **Verify** (check Telegram)

**That's it! Your 24/7 market monitoring is live!** 🚀

---

## 📈 Optimization Tips

### For Best Results
- ✅ Use **Groq** for AI (free and fast)
- ✅ Get both **NewsAPI** and **NewsData** (more coverage)
- ✅ Enable **Finnhub** for real-time WebSocket
- ✅ Run on **Docker** for reliability
- ✅ Deploy to **cloud** for 24/7 uptime

### Performance Tuning
- Start with default settings
- Monitor for 1 day
- Adjust cooldowns based on message volume
- Fine-tune intervals for your trading style

### Security
- Never share your `.env` file
- Keep API keys secret
- Use separate bots for different channels
- Regularly update dependencies

---

**Ready to level up your trading?** 🎯📊💰

👉 **Next Step**: Choose your platform and get started!

- Windows → [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)
- Docker → Run `docker-compose up -d`
- Linux → Run `./start_bot.sh`
- Cloud → See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
