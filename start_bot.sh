#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# 24/7 Market Monitoring Bot - Linux/Mac Startup Script
# ═══════════════════════════════════════════════════════════════════════

set -e

echo ""
echo "========================================================================"
echo "  24/7 Market Monitoring Bot - Starting..."
echo "========================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.12 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "[ERROR] Python $PYTHON_VERSION is too old"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    echo ""
    echo "Run: cp .env.example .env && nano .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "[INFO] Installing/updating dependencies..."
pip install -r requirements.txt

# Start the bot
echo ""
echo "========================================================================"
echo "  Bot is starting... Press Ctrl+C to stop"
echo "========================================================================"
echo ""

python unified_24x7_worker.py

# If bot exits, show message
echo ""
echo "========================================================================"
echo "  Bot has stopped"
echo "========================================================================"
