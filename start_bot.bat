@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM 24/7 Market Monitoring Bot - Windows Startup Script
REM ═══════════════════════════════════════════════════════════════════════

echo.
echo ========================================================================
echo   24/7 Market Monitoring Bot - Starting...
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.12 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure your API keys
    echo.
    echo Run: copy .env.example .env
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist .venv (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Start the bot
echo.
echo ========================================================================
echo   Bot is starting... Press Ctrl+C to stop
echo ========================================================================
echo.

python unified_24x7_worker.py

REM If bot exits, show message
echo.
echo ========================================================================
echo   Bot has stopped
echo ========================================================================
pause
