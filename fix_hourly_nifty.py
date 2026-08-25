import re
with open('unified_24x7_worker.py', 'r', encoding='utf-8') as f:
    content = f.read()

hourly_code = """
            # Intraday Hourly Nifty & Stock Options Alert (between 10:00 AM and 3:00 PM IST, at the top of the hour)
            if ist_now.weekday() < 5 and 10 <= ist_now.hour <= 15 and 0 <= ist_now.minute <= 5:
                if state.can_send_message(f"indian_hourly_nifty_{ist_now.hour}", 3500): # Once per hour
                    try:
                        print(f"[INDIAN] Running Hourly Nifty Options scan for {ist_now.hour}:00...")
                        import indian_scoring as iscoring
                        
                        # 1. Nifty Options
                        report = iscoring.fetch_nifty_sensex_oi_report()
                        nifty_lines = []
                        for item in report.get("top_oi_buildup", []):
                            if "NIFTY" in item["contract"]:
                                nifty_lines.append(f"dY' {item['contract']} - PCR: {item.get('pcr', 'N/A')} - Status: {item.get('status', '')}")
                        
                        nifty_msg = ""
                        if nifty_lines:
                            nifty_msg = "dY"- *LIVE HOURLY NIFTY OPTION SETUP*\n\n" + "\n".join(nifty_lines[:3]) + "\n\n_Market internals suggest momentum in these zones._"
                        
                        # 2. Stock Options
                        candidates = iscoring.scan_breakout_candidates("NSE")
                        stock_c = None
                        for c in candidates:
                            if c.get("option_contract") and c.get("option_contract") != "N/A":
                                stock_c = c
                                break
                        
                        if not stock_c and candidates:
                            stock_c = candidates[0]
                            
                        stock_msg = ""
                        if stock_c:
                            ticker = stock_c["ticker"]
                            status = stock_c["status"]
                            option = stock_c.get("option_contract", f"{ticker} CE/PE")
                            premium = stock_c.get("option_premium", "10-20")
                            
                            stock_msg = f"dY' *LIVE HOURLY STOCK OPTION SIGNAL*\n\n" \
                                        f"dY" Asset: *{ticker}*\n" \
                                        f"dY"S Status: {status}\n" \
                                        f"dY"- Contract: *{option}*\n" \
                                        f",1 Entry Premium: {premium}\n" \
                                        f"\n_Automated Intraday Scan - Trade with strict risk management!_"
                        
                        final_msg = ""
                        if nifty_msg and stock_msg:
                            final_msg = nifty_msg + "\n\n" + stock_msg
                        elif nifty_msg:
                            final_msg = nifty_msg
                        elif stock_msg:
                            final_msg = stock_msg
                            
                        if final_msg:
                            await broadcast_message(bot, final_msg, parse_mode="Markdown")
                            state.record_message(f"indian_hourly_nifty_{ist_now.hour}")
                            print(f"[INDIAN] Hourly Nifty options alert broadcasted to Telegram for {ist_now.hour}:00")
                    except Exception as hr_err:
                        print(f"[INDIAN] Hourly options alert broadcast failed: {hr_err}")
"""

# Insert it before the "Pre-Market Options Breakout Report"
content = content.replace("            # Pre-Market Options Breakout Report", hourly_code + "\n            # Pre-Market Options Breakout Report")

with open('unified_24x7_worker.py', 'w', encoding='utf-8') as f:
    f.write(content)
