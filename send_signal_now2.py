import asyncio
import main
import indian_scoring as iscoring
from telegram import Bot

async def trigger():
    bot = Bot(token=main.BOT_TOKEN)
    
    # 1. Nifty Signal
    report = iscoring.fetch_nifty_sensex_oi_report()
    nifty_lines = []
    for item in report.get("top_oi_buildup", []):
        if "NIFTY" in item["contract"]:
            nifty_lines.append(f"  {item['contract']} - PCR: {item.get('pcr', 'N/A')} - Status: {item.get('status', '')}")
            
    nifty_msg = "*LIVE NIFTY OPTION SETUP*\n\n" + "\n".join(nifty_lines[:3]) + "\n\n_Market internals suggest strong momentum in these zones._"
    print("Sending Nifty Signal...")
    await main.broadcast(bot, nifty_msg)
    
    # 2. Stock Signal
    candidates = iscoring.scan_breakout_candidates("NSE")
    stock_c = None
    for c in candidates:
        if c.get("option_contract") and c.get("option_contract") != "N/A":
            stock_c = c
            break
            
    if not stock_c and candidates:
        stock_c = candidates[0]
        
    if stock_c:
        ticker = stock_c["ticker"]
        status = stock_c["status"]
        option = stock_c.get("option_contract", f"{ticker} CE/PE")
        premium = stock_c.get("option_premium", "10-20")
        
        stock_msg = f"*LIVE STOCK OPTION SIGNAL*\n\n" \
                    f"Asset: *{ticker}*\n" \
                    f"Status: {status}\n" \
                    f"Contract: *{option}*\n" \
                    f"Entry Premium: {premium}\n" \
                    f"\n_Automated Breakout Scan - Trade with strict risk management!_"
                    
        print("Sending Stock Signal...")
        await main.broadcast(bot, stock_msg)

if __name__ == "__main__":
    asyncio.run(trigger())
