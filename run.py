"""Run a single fetch-and-send cycle (used by GitHub Actions)."""

import asyncio
import json
import os
import sys

from telegram import Bot

import ai_agent
import main as _main
from main import (
    BOT_TOKEN,
    _price_str,
    broadcast,
    fetch_current_prices,
    load_seen_keys,
    load_signal_log,
    run_worker_cycle,
    save_seen_keys,
    validate_config,
)

_AI_COUNTER_FILE = os.path.join(os.path.dirname(__file__), ".ai_cycle_counter")


def _read_counter() -> int:
    try:
        with open(_AI_COUNTER_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return 0


def _write_counter(n: int) -> None:
    with open(_AI_COUNTER_FILE, "w") as f:
        f.write(str(n))


async def run_ai_cycle(bot: Bot) -> None:
    cycle = _read_counter() + 1
    _write_counter(cycle)

    time_str = __import__("datetime").datetime.now(
        __import__("datetime").timezone(__import__("datetime").timedelta(hours=5, minutes=30))
    ).strftime("%H:%M IST")

    # Rotate assets for AI market update once every 8 cycles (every 2 hours) to avoid BTC spamming
    if cycle % 8 == 0:
        assets = ["EUR/USD", "XAU/USD", "US100", "BTC/USD"]
        asset = assets[(cycle // 8) % len(assets)]
        try:
            prices = fetch_current_prices()
            price = prices.get(asset)
            ai_update = ai_agent.generate_asset_market_update(asset, prices)
            if ai_update:
                block = ai_agent.format_asset_market_update(asset, ai_update, price)
                if block:
                    await broadcast(bot, block)
                    print(f"[AI] {asset} market update sent at {time_str}")
        except Exception as e:
            print(f"[AI] {asset} update failed: {e}")

    # Generate rotating trade suggestions every 12 cycles (every 3 hours)
    if cycle % 12 == 0:
        assets_sug = ["EUR/USD", "XAU/USD", "US100", "BTC/USD"]
        asset = assets_sug[(cycle // 12) % len(assets_sug)]
        try:
            if asset == "BTC/USD":
                btc_sug = ai_agent.generate_btc_trade_suggestion()
                if btc_sug:
                    block = ai_agent.format_btc_signal_block(btc_sug)
                    await broadcast(bot, block)
                    print(f"[AI] BTC trade suggestion sent at {time_str}")
            else:
                prices = fetch_current_prices()
                price = prices.get(asset)
                ai_update = ai_agent.generate_asset_market_update(asset, prices)
                if ai_update:
                    block = ai_agent.format_asset_market_update(asset, ai_update, price)
                    if block:
                        await broadcast(bot, block)
                        print(f"[AI] {asset} trade suggestion sent at {time_str}")
        except Exception as e:
            print(f"[AI] {asset} trade suggestion failed: {e}")

    # Educational tip every 6 cycles
    if cycle % 6 == 0:
        try:
            signals = load_signal_log()[-20:]
            tip = ai_agent.generate_market_education_tip(signals)
            if tip:
                await broadcast(bot, f"🧠 *AI Education Tip*\n\n{tip}")
                print(f"[AI] Education tip sent at {time_str}")
        except Exception as e:
            print(f"[AI] Education tip failed: {e}")

    # Market snapshot every 4 cycles
    if cycle % 4 == 0:
        try:
            prices = fetch_current_prices()
            snapshot_lines = [
                f"📸 *AI Market Snapshot* — {time_str}",
                f"━━━━━━━━━━━━━━━━━━",
            ]
            for pair in ["XAU/USD", "EUR/USD", "GBP/USD", "BTC/USD", "ETH/USD",
                         "US100", "US30", "DXY", "NIFTY", "WTI", "US10Y"]:
                p = prices.get(pair)
                if p:
                    snapshot_lines.append(f"  {pair}: {_price_str(p, pair)}")
            snapshot_lines.append("")
            enh = ai_agent.enhance_message_for_trader_levels(
                "\n".join(snapshot_lines), "intermediate",
            )
            snapshot_lines.append(f"💡 {enh}")
            await broadcast(bot, "\n".join(snapshot_lines))
            print(f"[AI] Market snapshot sent at {time_str}")
        except Exception as e:
            print(f"[AI] Market snapshot failed: {e}")

    print(f"[AI] Cycle {cycle} completed at {time_str}")


async def run_once() -> int:
    missing = validate_config()
    if missing:
        print(f"[ERROR] Missing: {', '.join(missing)}")
        return 1

    bot = Bot(BOT_TOKEN)
    seen_keys = load_seen_keys()
    _main._subscribers = _main.load_subscribers()
    _main._backfill_subscribers_from_updates()
    print(f"Loaded {len(seen_keys)} previously sent article keys.")
    print(f"Loaded {len(_main._subscribers)} subscriber(s).")

    sent = await run_worker_cycle(bot, seen_keys)
    save_seen_keys(seen_keys)
    print(f"News cycle complete. Sent {sent} message(s).")

    await run_ai_cycle(bot)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_once()))
