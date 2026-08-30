# -*- coding: utf-8 -*-
import asyncio
import time
import subprocess
import os
import sys

import main
import single_pass_worker
import paper_trader
from telegram import Bot

def git_sync_state():
    print("[GIT] Syncing state to repository...")
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        
        # Add files
        subprocess.run(["git", "add", "--ignore-errors", "sent_articles.json", "worker_24x7_state.json", "signal_log.json", "momentum_db.sqlite", "paper_trades.json"], check=False)
        
        # Commit
        res = subprocess.run(["git", "commit", "-m", "chore: sync state [skip ci]"], capture_output=True, text=True)
        if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
            print("[GIT] No changes to sync.")
            return

        # Pull rebase and push
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
        push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        print(f"[GIT] Push result: {push_res.stdout} {push_res.stderr}")
    except Exception as e:
        print(f"[GIT] Error during sync: {e}")

async def continuous_loop():
    print("[WORKER] Starting 24/7 Continuous GitHub Worker...")
    bot = Bot(token=main.BOT_TOKEN)
    
    start_time = time.time()
    # Run for 5 hours and 45 minutes to safely avoid GitHub's 6-hour hard limit
    max_duration = (5 * 3600) + (45 * 60)
    
    while True:
        cycle_start = time.time()
        if cycle_start - start_time >= max_duration:
            print("[WORKER] Approaching 6-hour limit. Shutting down cleanly to allow next workflow to take over.")
            break
            
        print(f"\n--- Starting Cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        seen_keys = main.load_seen_keys()
        
        try:
            sent = await main.run_worker_cycle(bot, seen_keys, silent_init=False)
            print(f"[WORKER] Sent {sent} news/signal messages.")
        except Exception as e:
            print(f"[WORKER] Error in run_worker_cycle: {e}")
        finally:
            main.save_seen_keys(seen_keys)
            
        print("[WORKER] Running market monitors...")
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
            print(f"[WORKER] Error in market monitors: {e}")
                
        single_pass_worker.state.save()
        
        # Sync state immediately after cycle completes
        git_sync_state()
        
        elapsed = time.time() - cycle_start
        sleep_time = max(0, 1500 - elapsed) # 25 minutes (1500 seconds)
        print(f"[WORKER] Cycle complete in {elapsed:.1f}s. Sleeping for {sleep_time:.1f}s...")
        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(continuous_loop())
