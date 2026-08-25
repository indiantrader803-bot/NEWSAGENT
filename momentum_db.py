import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("MOMENTUM_DB_PATH", "momentum_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Candles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume REAL NOT NULL
    )
    """)

    # Signals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        type TEXT NOT NULL,
        entry REAL NOT NULL,
        sl REAL NOT NULL,
        trail REAL,
        status TEXT NOT NULL,
        timestamp DATETIME NOT NULL
    )
    """)

    # Trades Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        broker TEXT NOT NULL,
        orderId TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        entry REAL NOT NULL,
        exit REAL,
        pnl REAL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL,
        timestamp DATETIME NOT NULL
    )
    """)

    # Strategy Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategy_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        event TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def log_strategy_event(symbol, event, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO strategy_logs (symbol, event, message, timestamp) VALUES (?, ?, ?, ?)",
        (symbol, event, message, datetime.utcnow())
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
