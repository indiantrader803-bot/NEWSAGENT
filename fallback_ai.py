import yfinance as yf
import json
import numpy as np

def generate_algorithmic_ta(symbol, price_data_str=None):
    tk = yf.Ticker(symbol)
    hist = tk.history(period="60d")
    if hist.empty:
        return None
        
    close = hist["Close"]
    curr = float(close.iloc[-1])
    sma20 = float(close.rolling(20).mean().iloc[-1])
    sma50 = float(close.rolling(50).mean().iloc[-1])
    high52 = float(close.max())
    low52 = float(close.min())
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = float((100 - (100 / (1 + rs))).iloc[-1])
    
    direction = "BULLISH"
    if curr < sma20 and rsi < 50:
        direction = "BEARISH"
    elif curr > sma20 and rsi > 50:
        direction = "BULLISH"
    else:
        direction = "NEUTRAL"
        
    if direction == "BULLISH":
        sl = curr * 0.98
        tp1 = curr + ((curr - sl) * 5)
        tp2 = curr + ((curr - sl) * 10)
        reason = f"Price ({curr:.2f}) is trending above SMA20 ({sma20:.2f}) with supportive RSI ({rsi:.1f}). Upward continuation expected."
    elif direction == "BEARISH":
        sl = curr * 1.02
        tp1 = curr - ((sl - curr) * 5)
        tp2 = curr - ((sl - curr) * 10)
        reason = f"Asset broke below SMA20 support ({sma20:.2f}) with weak RSI ({rsi:.1f}). Downside targets activated."
    else:
        sl = curr * 0.99
        tp1 = curr * 1.05
        tp2 = curr * 1.10
        reason = f"Consolidation near {curr:.2f} with neutral RSI ({rsi:.1f}). Awaiting breakout."
        
    return {
        "direction": direction,
        "entry": f"{curr:.2f}",
        "sl": f"{sl:.2f}",
        "tp1": f"{tp1:.2f}",
        "tp2": f"{tp2:.2f}",
        "confidence": f"{int(min(85, max(45, (abs(rsi-50)*1.5) + 50)))}%",
        "reason": reason
    }
    
print(generate_algorithmic_ta("RELIANCE.NS"))
