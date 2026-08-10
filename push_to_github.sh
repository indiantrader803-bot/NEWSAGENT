#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# Push All 24/7 Market Bot Changes to GitHub
# ═══════════════════════════════════════════════════════════════════════

set -e

echo ""
echo "========================================================================"
echo "  Pushing 24/7 Market Bot to GitHub"
echo "========================================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git is not installed"
    echo "Install with: sudo apt install git (Linux) or brew install git (Mac)"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "[INFO] Not a git repository. Initializing..."
    git init
    echo "[INFO] Please add your GitHub remote:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/Forexsignal.git"
    exit 1
fi

echo "[INFO] Current branch:"
git branch --show-current
echo ""

echo "[INFO] Staging all changes..."
git add .
echo ""

echo "[INFO] Files to be committed:"
git status --short
echo ""

echo "[INFO] Creating commit..."
git commit -m "🚀 Major Upgrade: Complete 24/7 Market Monitoring Bot

Features:
✅ True 24/7 continuous operation (not scheduled cron)
✅ ALL markets monitored: Indian, US, Forex, Crypto, Commodities
✅ Real-time WebSocket alerts via Finnhub
✅ AI-powered analysis (Groq/OpenAI)
✅ News-backed trade signals
✅ VIX spike detection
✅ Economic calendar alerts
✅ Pre-market gap detection
✅ Crypto pump screening 24/7
✅ Smart rate limiting & anti-spam
✅ Auto-recovery from errors
✅ Persistent state management

New Files:
- unified_24x7_worker.py (Main 24/7 bot)
- Dockerfile & docker-compose.yml (Container deployment)
- START_HERE.md (Quick start guide)
- QUICKSTART_WINDOWS.md (5-minute setup)
- DEPLOYMENT_GUIDE.md (Complete manual)
- UPGRADE_SUMMARY.md (What's new)
- verify_news_flow.py (Testing script)
- start_bot.bat / start_bot.sh (Startup scripts)

Improvements:
- All news data flows to Telegram continuously
- Market-hours aware scheduling
- Real-time crash/volatility alerts
- Multi-level explanations (Beginner/Intermediate/Expert)
- Production-ready Docker deployment
- Comprehensive documentation

Bug Fixes:
- Fixed: Bot not running 24/7
- Fixed: Limited market coverage
- Fixed: No real-time alerts
- Fixed: Duplicate messages
- Fixed: No auto-recovery

Markets Now Covered 24/7:
🇮🇳 Indian Equity (NSE/BSE, Nifty, Sensex, stocks)
🇺🇸 US Markets (NASDAQ, Dow, S&P 500, US stocks)
💱 Forex (All major pairs, 24/5)
₿ Crypto (BTC, ETH, altcoins, 24/7)
🏆 Commodities (Gold, Silver, Crude Oil)

Deployment Options:
- Docker Compose (recommended)
- Render.com (one-click)
- Railway.app (auto-deploy)
- Local Python
- Linux systemd service" || echo "[WARNING] Nothing to commit"

echo ""
echo "========================================================================"
echo "  Pushing to GitHub..."
echo "========================================================================"
echo ""

# Get current branch
BRANCH=$(git branch --show-current)

git push -u origin "$BRANCH" || {
    echo ""
    echo "[ERROR] Push failed!"
    echo "Possible causes:"
    echo "1. Not authenticated with GitHub"
    echo "2. Remote URL incorrect"
    echo "3. No internet connection"
    echo "4. Repository doesn't exist"
    echo ""
    echo "Try: git push -u origin $BRANCH --force"
    exit 1
}

echo ""
echo "========================================================================"
echo "  ✅ SUCCESS! All changes pushed to GitHub"
echo "========================================================================"
echo ""
echo "Your 24/7 Market Bot is now on GitHub!"
echo ""
echo "Next steps:"
echo "1. Go to your GitHub repository"
echo "2. Check that all files are uploaded"
echo "3. Update README badges if needed"
echo "4. Configure GitHub Secrets for deployment"
echo "5. Deploy to Render.com or your preferred platform"
echo ""
