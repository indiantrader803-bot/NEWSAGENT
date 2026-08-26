# -*- coding: utf-8 -*-
import asyncio
import time
import main
import unified_24x7_worker
from telegram import Bot

async def run_single_cycle():
    print("[CRON] Starting single market cycle...")
    bot = Bot(token=main.BOT_TOKEN)
    
    seen_keys = main.load_seen_keys()
    try:
        sent = await main.run_worker_cycle(bot, seen_keys, silent_init=False)
        print(f"[CRON] Sent {sent} news/signal messages.")
    except Exception as e:
        print(f"[CRON] Error in run_worker_cycle: {e}")
    finally:
        main.save_seen_keys(seen_keys)
        
    from datetime import datetime, timezone, timedelta
    ist_now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    if ist_now.weekday() < 5 and 9 <= ist_now.hour <= 15:
        try:
            import indian_scoring as iscoring
            intel = iscoring.get_full_intel(exchange="NSE")
            graded_signals = intel.get("top_graded_signals", [])
            print(f"[CRON] Found {len(graded_signals)} Indian Graded Signals")
            
            for sig in graded_signals:
                strike = sig.get('strike')
                direction = sig.get('direction')
                score = sig.get('score')
                headline = sig.get('headline')
                
                unique_key = f"live_graded_{ist_now.date()}_{strike}_{direction}"
                if unified_24x7_worker.state.can_send_message(unique_key, 86400):
                    msg = (
                        f"\U0001f3af <b>TOP SIGNALS - GRADED LIVE</b> \U0001f3af\n"
                        f"-------------------------\n"
                        f"\U0001f4c8 <b>{strike}</b> [{direction}]\n"
                        f"\U0001f4ca Score: {score}/100\n"
                        f"\U0001f4a1 {headline}\n"
                        f"-------------------------\n"
                        f"\u26a0\ufe0f <i>Fast Execution Required</i>"
                    )
                    from send_signal_now import broadcast_message
                    await broadcast_message(bot, msg, parse_mode="HTML")
                    unified_24x7_worker.state.record_message(unique_key)
        except Exception as e:
            print(f"[CRON] Error in Indian Graded Signals: {e}")
            
    unified_24x7_worker.state.save()
    print("[CRON] Cycle complete.")

if __name__ == "__main__":
    asyncio.run(run_single_cycle())
