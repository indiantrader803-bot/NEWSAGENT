import time
import asyncio
import traceback
import github_cron_worker

async def main():
    print("[KOYEB WORKER] Starting continuous 24/7 background worker...")
    while True:
        try:
            print(f"\n[KOYEB WORKER] Triggering market cycle at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
            await github_cron_worker.run_single_cycle()
            print("[KOYEB WORKER] Cycle completed successfully.")
        except Exception as e:
            print(f"[KOYEB WORKER] Error during cycle: {e}")
            traceback.print_exc()
            
        print("[KOYEB WORKER] Sleeping for 15 minutes until next scan...")
        await asyncio.sleep(15 * 60)

if __name__ == "__main__":
    asyncio.run(main())
