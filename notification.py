"""Simple notification helpers (Telegram) used by autotrade.

This module avoids importing `main` to prevent circular imports.
It uses the Telegram Bot HTTP API via `requests`.
"""
from typing import Optional
import os
import requests


def send_telegram_alert(text: str, chat_id: Optional[str] = None) -> bool:
    token = os.getenv("BOT_TOKEN") or os.getenv("BOT_TOKEN2")
    if not token:
        return False
    chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not chat:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False
