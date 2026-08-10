# 24/7 Comprehensive Market Monitoring Bot 🚀

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Professional-grade 24/7 market monitoring system** that sends real-time Telegram alerts for Indian equity, US stocks, Forex, Crypto, and Commodities markets.

---

## 🎯 What This Bot Does

This **upgraded 24/7 bot** continuously monitors **ALL major markets** and sends intelligent, real-time Telegram alerts:

### 🇮🇳 Indian Markets
- **NSE/BSE Live Updates**: Nifty, Sensex, Bank Nifty, India VIX
- **Top Stocks**: RELIANCE, TCS, HDFC, INFY, ICICI, etc.
- **Intraday Signals**: Real-time buy/sell opportunities
- **Options Strategies**: PCR-based Nifty/Sensex options suggestions
- **Pre-Market Alerts**: GIFT Nifty gap warnings before market opens

### 🇺🇸 US Markets
- **Major Indices**: NASDAQ (US100), Dow Jones (US30), S&P 500
- **Top Tech Stocks**: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META
- **Movers Alert**: Top gainers and losers in real-time
- **After-Hours Monitoring**: Extended trading hours coverage

### 💱 Forex (24/5 Coverage)
- **Major Pairs**: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, etc.
- **Cross Pairs**: EUR/GBP, GBP/JPY, AUD/JPY, etc.
- **AI-Powered Analysis**: News-backed trade setups with entry/TP/SL
- **Economic Calendar**: Pre-event alerts 3-7 minutes before releases
- **Central Bank Monitoring**: Fed, ECB, BoE, BoJ, RBI decisions

### ₿ Cryptocurrency (24/7 Coverage)
- **Major Coins**: BTC, ETH, SOL, XRP, ADA, DOGE, DOT, AVAX, LINK
- **Altcoin Pump Detection**: Early signals for trending altcoins
- **Volume Surge Alerts**: 24h volume change monitoring
- **Reversal Signals**: Oversold coins showing recovery
- **News-Backed Analysis**: Trade setups based on verified crypto news

### 🏆 Commodities
- **Precious Metals**: Gold (XAU/USD), Silver (XAG/USD)
- **Energy**: Crude Oil (WTI), Brent Oil
- **AI Analysis**: Macro-driven commodity trade setups

### 🚨 Real-Time Alerts
- **VIX Spike Detection**: Early volatility warnings
- **Crash Keywords**: Instant alerts on market crashes
- **Sharp Price Movements**: Real-time drop/surge detection
- **Economic Calendar**: High-impact event warnings
- **Breaking News**: Verified market-moving news

---

## 🌟 Key Upgrades (Why 24/7 Now Works!)

### ✅ **Previously**: Scheduled GitHub Actions (every 15-30 min)
### ✅ **Now**: True 24/7 continuous operation with:

1. **Parallel Market Monitoring**: Multiple async tasks for each market
2. **WebSocket Real-Time Data**: Finnhub live price feeds
3. **Smart Market Hours Detection**: More alerts during active trading
4. **Intelligent Rate Limiting**: Anti-spam with cooldown periods
5. **Persistent State Management**: Survives restarts without duplicate messages
6. **Auto-Recovery**: Automatic reconnection on errors
7. **Docker Ready**: Production-grade containerization
8. **Multi-Bot Support**: Up to 3 Telegram bots for redundancy

---

## 🚀 Quick Start (3 Minutes)

### Using Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Forexsignal

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 3. Start the 24/7 bot
docker-compose up -d

# 4. View logs
docker-compose logs -f market-bot-24x7
```

### Using Python (Local Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
cp .env.example .env
nano .env

# 3. Run the 24/7 worker
python unified_24x7_worker.py
```

---

## 📋 Required Environment Variables

```env
# Telegram (Required)
BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=@your_channel_or_chat_id

# News APIs (At least one required)
NEWS_API_KEY=your_newsapi_key
NEWSDATA_API_KEY=your_newsdata_key

# AI APIs (At least one required for AI features)
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Market Data
FINNHUB_API_KEY=your_finnhub_key  # For real-time WebSocket
```

### Optional (For Redundancy)

```env
BOT_TOKEN2=second_bot_token        # Backup bot
BOT_TOKEN3=third_bot_token         # Third bot
TELEGRAM_CHAT_ID3=alternate_chat_id
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 24/7 Market Monitoring Bot                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Indian Market│  │  US Markets  │  │ Forex Signals│    │
│  │   Monitor    │  │   Monitor    │  │   Generator  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │Crypto Screener│ │ Commodities  │  │  Realtime    │    │
│  │   (24/7)     │  │   Monitor    │  │   Alerts     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                          │                                  │
│                  ┌───────▼───────┐                         │
│                  │  Telegram API │                         │
│                  │   (3 Bots)    │                         │
│                  └───────────────┘                         │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         WebSocket (Finnhub Real-Time Data)         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │      State Management (Persistent Storage)         │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Message Examples

### Indian Market Update
```
🇮🇳 Indian Market Update
━━━━━━━━━━━━━━━━━━
Nifty 50: 19,850.25 (+120.50 | +0.61%)
Sensex: 66,450.30 (+380.20 | +0.58%)
Bank Nifty: 44,120.10 (-50.30 | -0.11%)
India VIX: 12.45 (+0.32 | +2.64%)

Top Gainers:
  + RELIANCE: 2,456.75 (+3.2%)
  + TCS: 3,201.50 (+2.8%)
  + HDFC: 2,750.20 (+2.1%)
```

### Crypto Pump Alert
```
📡 CryptoSignal Pro  |  AI PUMP WATCH

SOL  ·  🟢 BUY  ·  H1
Binance · Spot

━━━━━━━━━━━━━━━━━━
📌 Entry:      $21.4500
🛑 Stop Loss:  $20.8065  (-3.0%)
🎯 TP 1:       $22.5225  (+5.0%)
🎯 TP 2:       $23.5950  (+10.0%)
⚖️ R:R:        1 : 3.5

📊 Market Data
  24h Change:  +2.4%
  YTD:         -45.6%
  24h Vol Δ:   +78%
  RSI:         42  (MEDIUM risk)

🤖 AI Analysis: Oversold reversal showing volume surge...
```

---

## 🛠️ Configuration Options

### Monitoring Intervals

```env
CHECK_INTERVAL_FAST=30           # Active trading hours (30s)
CHECK_INTERVAL_SLOW=120          # Off-peak hours (2min)
INDIAN_MARKET_INTERVAL=60        # Indian market updates (1min)
US_MARKET_INTERVAL=60            # US market updates (1min)
FOREX_SIGNAL_INTERVAL=600        # Forex signals (10min)
CRYPTO_CHECK_INTERVAL=300        # Crypto screening (5min)
```

### Message Rate Limiting

```env
MESSAGE_COOLDOWN=120             # 2 min between similar messages
```

---

## 📖 Full Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Complete deployment instructions
- **[API Configuration](docs/API_SETUP.md)**: How to get API keys
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Advanced Configuration](docs/ADVANCED.md)**: Fine-tuning and customization

---

## 🎓 How to Get API Keys

### Telegram Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot: `/newbot`
3. Copy the bot token
4. Add bot to your channel as admin
5. Get chat ID: Forward a message to [@userinfobot](https://t.me/userinfobot)

### News APIs
- **NewsAPI**: [newsapi.org](https://newsapi.org/) (Free: 100 requests/day)
- **NewsData**: [newsdata.io](https://newsdata.io/) (Free: 200 requests/day)

### AI APIs
- **Groq**: [console.groq.com](https://console.groq.com/) (Free tier available)
- **OpenAI**: [platform.openai.com](https://platform.openai.com/) (Pay-as-you-go)

### Market Data
- **Finnhub**: [finnhub.io](https://finnhub.io/) (Free: 60 API calls/minute)
- **yfinance**: No API key needed (free Yahoo Finance data)

---

## 🐳 Docker Deployment

### Build & Run

```bash
# Build image
docker build -t market-bot-24x7 .

# Run container
docker run -d \
  --name forex-bot \
  --restart unless-stopped \
  --env-file .env \
  market-bot-24x7
```

### Docker Compose (Recommended)

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

---

## 📈 Monitoring & Logs

### View Real-Time Logs

```bash
# All logs
docker-compose logs -f

# Filter by market
docker-compose logs -f | grep '\[INDIAN\]'
docker-compose logs -f | grep '\[CRYPTO\]'
```

### Health Check

```bash
# Check container status
docker ps | grep forex-bot

# Check state file
ls -lh worker_24x7_state.json
```

---

## 🔧 Troubleshooting

### Bot Not Sending Messages

1. **Verify bot token**: Test with [@BotFather](https://t.me/botfather)
2. **Check chat ID**: Ensure bot is admin in channel
3. **Review logs**: `docker-compose logs -f`
4. **Test connection**:
   ```bash
   docker exec forex-bot python -c "from telegram import Bot; import os; print(Bot(os.getenv('BOT_TOKEN')).get_me())"
   ```

### High CPU Usage

- Increase intervals in `.env`
- Reduce concurrent monitors
- Check for infinite loops in logs

### Missing Alerts

- Check market hours (some monitors only run during trading)
- Review cooldown settings
- Clear state: `rm worker_24x7_state.json && docker-compose restart`

---

## 🚦 Old vs New System

| Feature | Old (GitHub Actions) | New (24/7 Worker) |
|---------|---------------------|------------------|
| **Operation** | Scheduled (15-30 min) | Continuous 24/7 |
| **Real-time** | ❌ No | ✅ Yes (WebSocket) |
| **Market Hours** | ❌ Unaware | ✅ Smart scheduling |
| **Multi-market** | ⚠️ Limited | ✅ All markets |
| **Recovery** | ⚠️ Manual | ✅ Automatic |
| **Scalability** | ❌ Limited | ✅ Production-ready |
| **Alerts** | ⚠️ Delayed | ✅ Instant |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## ⭐ Support

If this bot helps you, please:
- ⭐ Star this repository
- 📢 Share with other traders
- 🐛 Report bugs via Issues
- 💡 Suggest features

---

## 📞 Contact

For support or questions:
- GitHub Issues
- [Your contact info]

---

**Built with ❤️ for traders worldwide** 🌍
