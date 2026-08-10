# 24/7 Market Monitoring Bot - Deployment Guide

## 🚀 Overview

This upgraded bot monitors **ALL markets 24/7** and sends real-time Telegram alerts for:

- 🇮🇳 **Indian Equity Markets**: NSE/BSE (Nifty, Sensex, Bank Nifty, top stocks)
- 🇺🇸 **US Markets**: NASDAQ, Dow Jones, S&P 500, US stocks
- 💱 **Forex**: All major currency pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- ₿ **Cryptocurrencies**: Bitcoin, Ethereum, Solana, XRP, Cardano, Dogecoin, altcoins
- 🏆 **Commodities**: Gold (XAU/USD), Silver, Crude Oil, Brent
- 📊 **Intraday Signals**: Real-time cash market signals

## 🎯 Key Features

### ✅ True 24/7 Operation
- Continuous monitoring with intelligent scheduling
- Market-hours aware (sends more during active trading)
- Automatic recovery from errors
- Persistent state across restarts

### ✅ Multi-Market Coverage
- **Indian Market Hours** (9:15 AM - 3:30 PM IST): Live NSE/BSE updates, options suggestions
- **US Market Hours** (9:30 AM - 4:00 PM EST): NASDAQ, Dow Jones, S&P 500 updates
- **Forex** (24/5): Real-time signals and news-backed analysis
- **Crypto** (24/7): Pump detection, altcoin screening, BTC/ETH analysis
- **Commodities** (24/5): Gold, silver, crude oil signals

### ✅ Intelligent Alert System
- **VIX Spike Detection**: Alerts before market volatility
- **Crash Keywords**: Instant alerts on market-moving news
- **Economic Calendar**: Pre-event warnings (3-7 minutes before)
- **Pre-market Gap Detection**: GIFT Nifty gap alerts before NSE opens
- **Price Drop Detection**: Real-time sharp movement alerts

### ✅ AI-Powered Analysis
- News-backed trade suggestions (not generic hype)
- Multi-level explanations (Beginner/Intermediate/Experienced)
- Institutional-quality analysis
- Real-time market sentiment

### ✅ Rate Limiting & Anti-Spam
- Smart cooldown periods between similar messages
- Daily message caps per category
- Priority-based alert system
- Configurable intervals

---

## 📋 Deployment Options

### Option 1: Docker Compose (Recommended) ⭐

**Best for**: Production deployment, easy management, auto-restart

```bash
# 1. Clone/download the repository
cd Forexsignal

# 2. Configure environment variables
cp .env.example .env
nano .env  # Add your API keys

# 3. Build and start the container
docker-compose up -d

# 4. View logs
docker-compose logs -f market-bot-24x7

# 5. Stop the bot
docker-compose down
```

**Advantages:**
- ✅ Auto-restart on failure
- ✅ Resource limits
- ✅ Persistent state
- ✅ Easy updates
- ✅ Production-ready

---

### Option 2: Docker (Standalone)

```bash
# Build the image
docker build -t forex-bot-24x7 .

# Run the container
docker run -d \
  --name forex-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  forex-bot-24x7

# View logs
docker logs -f forex-bot
```

---

### Option 3: Local Python (Development)

**Best for**: Testing, development, debugging

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env file
cp .env.example .env
nano .env

# 3. Run the 24/7 worker
python unified_24x7_worker.py
```

**Note**: Use a process manager like `systemd`, `supervisor`, or `pm2` for production.

---

### Option 4: Cloud Deployment

#### **Render.com** (Free Tier Available)

1. Fork this repository
2. Connect to Render.com
3. Create a new **Background Worker**
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python unified_24x7_worker.py`
6. Add environment variables from `.env`
7. Deploy

#### **Railway.app**

1. Import project from GitHub
2. Add environment variables
3. Deploy automatically
4. Monitor logs in dashboard

#### **AWS/GCP/Azure**

Deploy as:
- **AWS ECS/Fargate**: Container service (recommended)
- **AWS EC2**: VM with Docker
- **Google Cloud Run**: Serverless container
- **Azure Container Instances**: Serverless Docker

---

## 🔧 Configuration

### Required Environment Variables

```env
# Telegram Bots (at least BOT_TOKEN required)
BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=@your_channel_or_chat_id

# Optional: Additional bots for redundancy
BOT_TOKEN2=optional_second_bot_token
BOT_TOKEN3=optional_third_bot_token
TELEGRAM_CHAT_ID3=optional_third_chat_id

# News APIs (at least one required)
NEWS_API_KEY=your_newsapi_key
NEWSDATA_API_KEY=your_newsdata_key

# AI APIs (at least one required for AI features)
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Market Data
FINNHUB_API_KEY=your_finnhub_key
MASSIVE_API_KEY=optional_massive_api_key
```

### Optional Configuration

```env
# Intervals (in seconds)
CHECK_INTERVAL_FAST=30           # Active market hours
CHECK_INTERVAL_SLOW=120          # Off-peak hours
NEWS_CHECK_INTERVAL=180          # News cycle
CRYPTO_CHECK_INTERVAL=300        # Crypto screening
INDIAN_MARKET_INTERVAL=60        # Indian market updates
US_MARKET_INTERVAL=60            # US market updates
FOREX_SIGNAL_INTERVAL=600        # Forex signals

# Message Cooldowns (in seconds)
MESSAGE_COOLDOWN=120             # Between similar messages

# News Provider
NEWS_PROVIDER=auto               # auto, newsapi, newsdata
LIVE_NEWS_ENABLED=true           # Enable RSS feeds
```

---

## 📊 Monitoring & Logs

### Docker Compose Logs

```bash
# View real-time logs
docker-compose logs -f market-bot-24x7

# View last 100 lines
docker-compose logs --tail=100 market-bot-24x7

# View logs since 1 hour ago
docker-compose logs --since 1h market-bot-24x7
```

### Health Checks

The bot includes built-in health checks:

```bash
# Check container health
docker inspect forex-signals-24x7 | grep -A 5 Health

# Check state file (indicates bot is running)
ls -lh worker_24x7_state.json
```

### Log Patterns

```
[INDIAN] Market snapshot sent
[US] Market snapshot sent
[FOREX] Sent 3 signals
[CRYPTO] Sent 2 pump alerts
[COMMODITIES] XAU/USD signal sent
[REALTIME] Sent 1 alerts
[BRIEFING] Morning briefing sent
[WEBSOCKET] Connected to Finnhub WebSocket
```

---

## 🛠️ Troubleshooting

### Bot Not Sending Messages

1. **Check API keys**: Ensure all keys are valid and not expired
2. **Verify Telegram bot**: Test bot with `/start` command
3. **Check chat ID**: Ensure `TELEGRAM_CHAT_ID` is correct (use @username or numeric ID)
4. **Review logs**: Look for error messages in logs
5. **Test network**: Ensure container can reach Telegram API

```bash
# Test Telegram connection
docker exec forex-signals-24x7 python -c "
from telegram import Bot
import os
bot = Bot(os.getenv('BOT_TOKEN'))
print(bot.get_me())
"
```

### High CPU/Memory Usage

1. **Increase cooldown intervals** in `.env`
2. **Reduce concurrent tasks** by commenting out monitors in `unified_24x7_worker.py`
3. **Check for memory leaks** in logs
4. **Restart container**: `docker-compose restart`

### WebSocket Disconnects

The bot auto-reconnects every 10 seconds. If persistent:

1. **Check Finnhub API key** validity
2. **Check network connectivity**
3. **Review Finnhub rate limits**

### Missing Alerts

1. **Check market hours**: Some monitors only run during trading hours
2. **Check cooldown periods**: Messages may be rate-limited
3. **Review state file**: `cat worker_24x7_state.json`
4. **Clear state** if needed: `rm worker_24x7_state.json && docker-compose restart`

---

## 🔄 Updates & Maintenance

### Update Bot Code

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup State Files

```bash
# Backup important state
tar -czf backup-$(date +%Y%m%d).tar.gz \
  sent_articles.json \
  signal_log.json \
  worker_24x7_state.json \
  crypto_screener_seen.json
```

### Reset Bot State

```bash
# Stop bot
docker-compose down

# Remove state files
rm -f sent_articles.json signal_log.json worker_24x7_state.json

# Restart
docker-compose up -d
```

---

## 📈 Performance Tuning

### For High-Volume Channels

Increase intervals to reduce message frequency:

```env
MESSAGE_COOLDOWN=300              # 5 minutes between similar messages
FOREX_SIGNAL_INTERVAL=1200        # 20 minutes for forex
CRYPTO_CHECK_INTERVAL=600         # 10 minutes for crypto
```

### For Real-Time Trading

Decrease intervals for faster alerts:

```env
CHECK_INTERVAL_FAST=15            # 15 seconds
INDIAN_MARKET_INTERVAL=30         # 30 seconds during market hours
MESSAGE_COOLDOWN=60               # 1 minute cooldown
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'        # Increase CPU
      memory: 1G         # Increase RAM
```

---

## 🎓 Usage Examples

### Monitor Logs in Real-Time

```bash
docker-compose logs -f | grep -E '\[(INDIAN|US|FOREX|CRYPTO|COMMODITIES)\]'
```

### Check Daily Message Count

```bash
docker exec forex-signals-24x7 python -c "
import json
with open('worker_24x7_state.json') as f:
    state = json.load(f)
    print(json.dumps(state.get('daily_message_count', {}), indent=2))
"
```

### Manual Test Run

```bash
docker exec -it forex-signals-24x7 python -c "
import asyncio
from unified_24x7_worker import broadcast_message
from telegram import Bot
import os

async def test():
    bot = Bot(os.getenv('BOT_TOKEN'))
    await broadcast_message(bot, '🧪 Test message from 24/7 bot')

asyncio.run(test())
"
```

---

## 🆘 Support & Contact

For issues, questions, or feature requests:

1. Check logs first: `docker-compose logs -f`
2. Review this guide
3. Check GitHub Issues (if applicable)
4. Contact: [Your contact info]

---

## 📄 License

[Your license information]

---

## 🙏 Credits

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [tradingview-screener](https://github.com/mnvoh/tradingview-screener)
- [Finnhub API](https://finnhub.io/)
- [News APIs](https://newsapi.org/)
- [Groq AI](https://groq.com/) / [OpenAI](https://openai.com/)
