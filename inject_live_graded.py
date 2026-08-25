import re

with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    content = f.read()

live_scan_logic = """
            # Live Graded Options Signals - IMMEDIATE BROADCAST (Scans every 5 minutes)
            if ist_now.weekday() < 5 and 9 <= ist_now.hour <= 15:
                if state.can_send_message("indian_live_graded_scan", 300):
                    try:
                        import indian_scoring as iscoring
                        intel = iscoring.get_full_intel(exchange="NSE")
                        graded_signals = intel.get("top_graded_signals", [])
                        
                        for sig in graded_signals:
                            strike = sig.get('strike')
                            direction = sig.get('direction')
                            score = sig.get('score')
                            headline = sig.get('headline')
                            
                            unique_key = f"live_graded_{ist_now.date()}_{strike}_{direction}"
                            
                            # Only broadcast if we haven't sent this exact strike/direction today
                            if state.can_send_message(unique_key, 86400):
                                msg = (
                                    f"?? <b>TOP SIGNALS — GRADED LIVE</b> ??\\n"
                                    f"?????????????????????????\\n"
                                    f"?? <b>{strike}</b> [{direction}]\\n"
                                    f"? Score: {score}/100\\n"
                                    f"?? {headline}\\n"
                                    f"?????????????????????????\\n"
                                    f"?? <i>Fast Execution Required</i>"
                                )
                                import asyncio
                                asyncio.create_task(broadcast_message(bot, msg, parse_mode="HTML"))
                                state.record_message(unique_key)
                                print(f"[INDIAN] Live Graded Signal broadcasted: {strike}")
                    except Exception as e:
                        print(f"[INDIAN] Live graded scan error: {e}")
                        
            # Intraday Hourly Nifty & Stock Options Alert (between 10:00 AM and 3:00 PM IST, at the top of the hour)"""

# We replace the comment "# Intraday Hourly Nifty..." with the block that includes the new live scanner just before it.
content = content.replace(
    "# Intraday Hourly Nifty & Stock Options Alert (between 10:00 AM and 3:00 PM IST, at the top of the hour)",
    live_scan_logic.strip()
)

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(content)
