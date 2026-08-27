import json
import os
from datetime import datetime, timezone
import main

PAPER_FILE = "paper_trades.json"

def load_trades():
    if not os.path.exists(PAPER_FILE):
        return []
    with open(PAPER_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_trades(trades):
    with open(PAPER_FILE, "w") as f:
        json.dump(trades, f, indent=4)

def open_virtual_trade(signal_data):
    """
    Called when a new signal is generated.
    signal_data is a dict containing: pair, direction, entry, tp1, tp2, sl, source
    """
    trades = load_trades()
    
    # Check if we already have an open trade for this pair
    for t in trades:
        if t["status"] == "OPEN" and t["pair"] == signal_data.get("pair"):
            return False # already open
            
    # Need numerical targets
    try:
        entry = float(signal_data["entry"])
        tp1 = float(signal_data["tp1"])
        sl = float(signal_data["sl"])
    except:
        return False

    if entry == 0.0:
        return False
        
    new_trade = {
        "trade_id": f"TR_{int(datetime.now().timestamp())}",
        "pair": signal_data["pair"],
        "direction": signal_data["direction"],
        "entry_price": entry,
        "tp1": tp1,
        "sl": sl,
        "status": "OPEN",
        "opened_at": datetime.now(timezone.utc).isoformat(),
        "closed_at": None,
        "exit_price": None,
        "pnl_pct": None,
        "source": signal_data.get("source", "unknown")
    }
    
    trades.append(new_trade)
    save_trades(trades)
    return new_trade

async def evaluate_open_trades(bot):
    """
    Checks live prices for all OPEN trades and closes them if they hit TP or SL.
    Sends a telegram message when a trade closes.
    """
    trades = load_trades()
    open_trades = [t for t in trades if t["status"] == "OPEN"]
    
    if not open_trades:
        return
        
    # Fetch latest prices for everything
    current_prices = main.fetch_current_prices()
    
    changed = False
    
    for t in open_trades:
        pair = t["pair"]
        current_price = current_prices.get(pair)
        
        if not current_price:
            continue
            
        direction = t["direction"].upper()
        entry = t["entry_price"]
        tp1 = t["tp1"]
        sl = t["sl"]
        
        closed = False
        exit_price = 0.0
        reason = ""
        
        if direction in ["BUY", "BULLISH"]:
            if current_price >= tp1:
                closed = True
                exit_price = current_price
                reason = "?? TARGET HIT"
            elif current_price <= sl:
                closed = True
                exit_price = current_price
                reason = "?? STOP LOSS HIT"
        elif direction in ["SELL", "BEARISH"]:
            if current_price <= tp1:
                closed = True
                exit_price = current_price
                reason = "?? TARGET HIT"
            elif current_price >= sl:
                closed = True
                exit_price = current_price
                reason = "?? STOP LOSS HIT"
                
        if closed:
            t["status"] = "CLOSED"
            t["closed_at"] = datetime.now(timezone.utc).isoformat()
            t["exit_price"] = exit_price
            
            # Calculate PnL %
            if direction in ["BUY", "BULLISH"]:
                pnl = ((exit_price - entry) / entry) * 100
            else:
                pnl = ((entry - exit_price) / entry) * 100
                
            t["pnl_pct"] = round(pnl, 2)
            changed = True
            
            # Send Telegram Alert
            emoji = "?" if pnl > 0 else "?"
            msg = (
                f"{emoji} *PAPER TRADE CLOSED* {emoji}\n"
                f"??????????????????\n"
                f"*{pair}* | {direction}\n"
                f"{reason}\n\n"
                f"?? *Entry:* {entry}\n"
                f"?? *Exit:*  {exit_price}\n"
                f"?? *PnL:*  {t['pnl_pct']}%"
            )
            try:
                await bot.send_message(chat_id=main.TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to send paper trade alert: {e}")
                
    if changed:
        save_trades(trades)
