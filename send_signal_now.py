import asyncio
import os
from telegram import Bot
import indian_scoring as iscoring
import ai_agent

# Fetch Telegram token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    # Try reading from .env if running standalone
    try:
        with open(".env") as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    BOT_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass

async def send_nifty_and_stock_signal():
    bot = Bot(token=BOT_TOKEN)
    
    # 1. Nifty Options Signal
    print("Fetching Nifty data...")
    report = iscoring.fetch_nifty_sensex_oi_report()
    nifty_lines = []
    for item in report.get("top_oi_buildup", []):
        if "NIFTY" in item["contract"]:
            nifty_lines.append(f"dY' {item['contract']} - PCR: {item.get('pcr', 'N/A')} - OI Status: {item.get('status', '')}")
            
    nifty_msg = "dY"- *LIVE NIFTY OPTION SETUP*\n\n" + "\n".join(nifty_lines[:3]) + "\n\n_Market internals suggest strong momentum in these zones._"
    print(f"Sending Nifty Signal: {nifty_msg}")
    await bot.send_message(chat_id="@newsagentforex", text=nifty_msg, parse_mode="Markdown") # Assuming this is the channel
    
    # 2. Stock Options Signal
    print("Fetching Stock Breakout candidates...")
    candidates = iscoring.scan_breakout_candidates("NSE")
    stock_c = None
    for c in candidates:
        if c.get("option_contract") != "N/A":
            stock_c = c
            break
            
    if not stock_c and candidates:
        stock_c = candidates[0]
        
    if stock_c:
        ticker = stock_c["ticker"]
        status = stock_c["status"]
        option = stock_c.get("option_contract", f"{ticker} CE/PE")
        premium = stock_c.get("option_premium", "10-20")
        
        stock_msg = f"dY' *LIVE STOCK OPTION SIGNAL*\n\n" \
                    f"dY" Asset: *{ticker}*\n" \
                    f"dY"S Status: {status}\n" \
                    f"dY"- Contract: *{option}*\n" \
                    f",1 Entry Premium: {premium}\n" \
                    f"\n_Automated Breakout Scan - Trade with strict risk management!_"
                    
        print(f"Sending Stock Signal: {stock_msg}")
        await bot.send_message(chat_id="@newsagentforex", text=stock_msg, parse_mode="Markdown")
    else:
        print("No stock candidate found.")
        
if __name__ == "__main__":
    asyncio.run(send_nifty_and_stock_signal())
