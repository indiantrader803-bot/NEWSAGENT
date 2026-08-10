# Quick Start Guide - Windows

## 🚀 Get Your Bot Running in 5 Minutes!

### Step 1: Install Python

1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Get API Keys

#### Telegram Bot (Required)
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy your bot token (looks like: `123456789:ABCdefGHIjklMNOpqrs`)
4. Add your bot to your channel as an admin

#### Get Your Channel ID
1. Message [@userinfobot](https://t.me/userinfobot)
2. Forward any message from your channel to the bot
3. Copy the chat ID (for channels it starts with `-100`)
   - Or use `@your_channel_name` format

#### News API (Required - Choose One)
- **NewsAPI**: Sign up at [newsapi.org](https://newsapi.org/) (Free: 100/day)
- **NewsData**: Sign up at [newsdata.io](https://newsdata.io/) (Free: 200/day)

#### AI API (Required - Choose One)
- **Groq**: Sign up at [console.groq.com](https://console.groq.com/) (FREE!)
- **OpenAI**: Sign up at [platform.openai.com](https://platform.openai.com/) (Paid)

#### Market Data (Optional but Recommended)
- **Finnhub**: Sign up at [finnhub.io](https://finnhub.io/) (Free: 60/min)

### Step 3: Configure Your Bot

1. Open the downloaded folder in File Explorer
2. Copy `.env.example` to `.env`
3. Open `.env` with Notepad
4. Fill in your API keys:

```env
# Required
BOT_TOKEN=paste_your_telegram_bot_token_here
TELEGRAM_CHAT_ID=@your_channel_name

# At least one news API
NEWS_API_KEY=paste_your_newsapi_key_here
# OR
NEWSDATA_API_KEY=paste_your_newsdata_key_here

# At least one AI API  
GROQ_API_KEY=paste_your_groq_key_here
# OR
OPENAI_API_KEY=paste_your_openai_key_here

# Optional but recommended
FINNHUB_API_KEY=paste_your_finnhub_key_here
```

5. Save and close `.env`

### Step 4: Start Your Bot!

#### Method 1: Double-Click (Easiest)
1. Double-click `start_bot.bat`
2. Wait for dependencies to install (first time only)
3. Bot will start automatically!

#### Method 2: Command Line
1. Open Command Prompt in the folder
2. Run:
   ```cmd
   start_bot.bat
   ```

### Step 5: Verify It's Working

Your Telegram channel should receive a startup message:
```
✅ 24/7 Market Bot Online
━━━━━━━━━━━━━━━━━━
Monitoring all markets:
🇮🇳 Indian Equity (NSE/BSE)
🇺🇸 US Stocks & Indices
💱 Forex (All major pairs)
₿ Crypto (BTC, ETH, Altcoins)
🏆 Commodities (Gold, Silver, Oil)
```

## 🎉 That's It! Your Bot is Now Running 24/7

### What Happens Next?

The bot will:
- ✅ Monitor Indian markets (9:15 AM - 3:30 PM IST)
- ✅ Monitor US markets (9:30 AM - 4:00 PM EST)  
- ✅ Monitor Forex 24/5
- ✅ Monitor Crypto 24/7
- ✅ Send real-time alerts and signals
- ✅ Generate AI-powered trade analysis

### Keeping It Running

**Option 1: Keep the window open**
- Just leave the Command Prompt window open
- Your PC must stay on

**Option 2: Run as Windows Service (Advanced)**
- Use NSSM (Non-Sucking Service Manager)
- Download from [nssm.cc](https://nssm.cc/)
- Install as service:
  ```cmd
  nssm install MarketBot "C:\path\to\python.exe" "C:\path\to\unified_24x7_worker.py"
  nssm start MarketBot
  ```

**Option 3: Use Docker (Recommended)**
- See main README for Docker instructions
- Best for servers or always-on PCs

## 🐛 Troubleshooting

### "Python is not recognized"
- Reinstall Python with "Add to PATH" checked
- Or add Python to PATH manually

### "pip is not recognized"
- Run: `python -m pip install -r requirements.txt`

### Bot starts but no messages
1. Check `.env` file - ensure no typos in API keys
2. Verify bot is admin in your Telegram channel
3. Test bot token:
   ```cmd
   python -c "from telegram import Bot; import os; from dotenv import load_dotenv; load_dotenv(); print(Bot(os.getenv('BOT_TOKEN')).get_me())"
   ```

### "Module not found" errors
- Delete `.venv` folder and run `start_bot.bat` again

### Bot crashes randomly
- Check internet connection
- Verify API keys haven't expired
- Look at error messages in console

## 📞 Need Help?

- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed docs
- Review [Troubleshooting section](DEPLOYMENT_GUIDE.md#troubleshooting)
- Open an issue on GitHub

## 🎓 Next Steps

Once your bot is running:

1. **Customize intervals** in `.env` to control message frequency
2. **Add multiple bots** for redundancy (`BOT_TOKEN2`, `BOT_TOKEN3`)
3. **Monitor logs** to see what's happening
4. **Fine-tune** based on your trading style

## 💡 Pro Tips

- Use **Groq AI** (free and fast) instead of OpenAI to save money
- Get **both NewsAPI and NewsData** for better news coverage
- Use **Finnhub** for real-time WebSocket alerts
- Keep your `.env` file secure (never share it!)
- Back up your state files regularly

---

**Enjoy your 24/7 market monitoring!** 🚀📈
