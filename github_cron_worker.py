# -*- coding: utf-8 -*-
import asyncio
import time
import main
import single_pass_worker
import paper_trader
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
        
    print("[CRON] Running market monitors...")
    try:
        await asyncio.gather(
            single_pass_worker.monitor_indian_market(bot),
            single_pass_worker.monitor_us_market(bot),
            single_pass_worker.monitor_forex_signals(bot),
            single_pass_worker.monitor_crypto_market(bot),
            single_pass_worker.monitor_commodities(bot),
            single_pass_worker.monitor_realtime_alerts(bot),
            paper_trader.evaluate_open_trades(bot)
        )
    except Exception as e:
        print(f"[CRON] Error in market monitors: {e}")
            
    single_pass_worker.state.save()
    
    # We must also sync the state back to unified_24x7_worker state file so it persists correctly 
    # (they use the same worker_24x7_state.json anyway because it's defined in the class).
    print("[CRON] Cycle complete.")

if __name__ == "__main__":
    asyncio.run(run_single_cycle())
