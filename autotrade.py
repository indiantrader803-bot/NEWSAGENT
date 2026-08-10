"""Simple autotrade service: selects broker adapter and places simulated orders.

Usage: set environment variables in your environment or `.env`:
- AUTOTRADE_ENABLED=1
- AUTOTRADE_MODE=paper|live  (paper uses DummyBroker)
- BROKER_PROVIDER=dummy|oanda|alpaca

This module intentionally implements a safe default (dummy/paper) broker.
"""
from typing import Optional
import os
from brokers import get_broker
import json
from datetime import datetime, timezone


AUTOTRADE_ENABLED = os.getenv("AUTOTRADE_ENABLED", "").strip() in {"1", "true", "yes"}
BROKER_PROVIDER = os.getenv("BROKER_PROVIDER", "dummy").strip().lower()
AUTOTRADE_MODE = os.getenv("AUTOTRADE_MODE", "paper").strip().lower()
MAX_UNITS_PER_TRADE = float(os.getenv("MAX_UNITS_PER_TRADE", "0").strip() or 0)
_LEVERAGE_RAW = os.getenv("LEVERAGE", "1:1").strip()

# Persistent file paths and safety limits
TRADES_FILE = os.getenv("AUTOTRADE_TRADES_FILE", "autotrade_trades.json")
LOSS_FILE = os.getenv("AUTOTRADE_LOSS_FILE", "autotrade_loss.json")
MAX_DAILY_LOSS = float(os.getenv("AUTOTRADE_MAX_DAILY_LOSS", "0").strip() or 0)


def parse_leverage(raw: str) -> float:
    """Parse leverage in forms like '1:5' or '5' into numeric multiplier (e.g. 5.0)."""
    if not raw:
        return 1.0
    raw = raw.strip()
    if ":" in raw:
        try:
            a, b = raw.split(":", 1)
            return float(b) / float(a) if float(a) != 0 else 1.0
        except Exception:
            return 1.0
    try:
        return float(raw)
    except Exception:
        return 1.0

LEVERAGE = parse_leverage(_LEVERAGE_RAW)


class AutoTrader:
    def __init__(self):
        # For now the factory will return DummyBroker for unknown providers
        self.broker = get_broker(BROKER_PROVIDER)
        # ensure daily loss file exists
        try:
            if not os.path.exists(LOSS_FILE):
                with open(LOSS_FILE, "w", encoding="utf-8") as f:
                    json.dump({"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "loss": 0.0}, f)
        except Exception:
            pass

    def place_trade(self, pair: str, direction: str, entry: float, tp1: float, tp2: float, sl: float, units: Optional[float] = None) -> dict:
        if not AUTOTRADE_ENABLED:
            return {"status": "disabled"}

        # Enforce daily loss limit
        if MAX_DAILY_LOSS and not self._daily_loss_allowed():
            return {"status": "rejected", "reason": f"MAX_DAILY_LOSS={MAX_DAILY_LOSS} exceeded"}

        side = "buy" if direction.lower().startswith("buy") else "sell"
        # Default units: 1000 if unspecified (paper)
        units = float(units) if units else 1000.0

        # Enforce per-trade maximum if configured (0 => no limit)
        if MAX_UNITS_PER_TRADE and units > MAX_UNITS_PER_TRADE:
            return {"status": "rejected", "reason": f"units {units} exceed MAX_UNITS_PER_TRADE={MAX_UNITS_PER_TRADE}"}

        # If a secondary TP is provided, split units according to AUTOTRADE_TP2_PCT
        tp2_pct_raw = os.getenv("AUTOTRADE_TP2_PCT", "0.5").strip()
        try:
            tp2_pct = float(tp2_pct_raw)
        except Exception:
            tp2_pct = 0.5

        results = []
        try:
            if tp2 and tp2_pct > 0 and tp2_pct < 1:
                units_tp2 = units * tp2_pct
                units_tp1 = units - units_tp2
                # Place partial order targeting tp1
                resp1 = self.broker.place_order(pair=pair, side=side, units=units_tp1, entry=entry, tp=tp1, sl=sl, leverage=LEVERAGE, tp2=None)
                # Place separate leg for tp2
                resp2 = self.broker.place_order(pair=pair, side=side, units=units_tp2, entry=entry, tp=tp2, sl=sl, leverage=LEVERAGE, tp2=tp2)
                results.extend([resp1, resp2])
            else:
                resp = self.broker.place_order(pair=pair, side=side, units=units, entry=entry, tp=tp1, sl=sl, leverage=LEVERAGE, tp2=tp2)
                results.append(resp)

            # persist trade record
            self._record_trade({
                "pair": pair,
                "side": side,
                "entry": entry,
                "tp1": tp1,
                "tp2": tp2,
                "sl": sl,
                "units": units,
                "results": results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return {"status": "ok", "orders": results}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def _record_trade(self, data: dict) -> None:
        try:
            path = os.getenv("AUTOTRADE_TRADES_FILE", "autotrade_trades.json")
            all_trades = []
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        all_trades = json.load(f)
                except Exception:
                    all_trades = []
            all_trades.append(data)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(all_trades, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _daily_loss_state(self) -> dict:
        try:
            if not os.path.exists(LOSS_FILE):
                return {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "loss": 0.0}
            with open(LOSS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "loss": 0.0}

    def _save_daily_loss_state(self, state: dict) -> None:
        try:
            with open(LOSS_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _daily_loss_allowed(self) -> bool:
        if not MAX_DAILY_LOSS or MAX_DAILY_LOSS <= 0:
            return True
        state = self._daily_loss_state()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if state.get("date") != today:
            # reset for new day
            state = {"date": today, "loss": 0.0}
            self._save_daily_loss_state(state)
            return True
        return float(state.get("loss", 0.0)) < float(MAX_DAILY_LOSS)

    def report_trade_pnl(self, order_id: str, pnl: float) -> None:
        # record realized PnL and update daily loss if pnl < 0
        try:
            # update trades file if exists
            path = os.getenv("AUTOTRADE_TRADES_FILE", "autotrade_trades.json")
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        all_trades = json.load(f)
                except Exception:
                    all_trades = []
                for t in all_trades:
                    # match by id in any placed order leg
                    updated = False
                    for o in t.get("results", []) if isinstance(t.get("results"), list) else []:
                        if o.get("id") == order_id:
                            o["realized_pnl"] = pnl
                            updated = True
                    if updated:
                        break
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(all_trades, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

            if pnl < 0 and MAX_DAILY_LOSS and MAX_DAILY_LOSS > 0:
                state = self._daily_loss_state()
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                if state.get("date") != today:
                    state = {"date": today, "loss": 0.0}
                state["loss"] = float(state.get("loss", 0.0)) + abs(float(pnl))
                self._save_daily_loss_state(state)
        except Exception:
            pass


_AUTOTRADER: AutoTrader | None = None


def get_autotrader() -> AutoTrader:
    global _AUTOTRADER
    if _AUTOTRADER is None:
        _AUTOTRADER = AutoTrader()
    return _AUTOTRADER


def place_trade(pair: str, direction: str, entry: float, tp1: float, tp2: float, sl: float, units: Optional[float] = None) -> dict:
    trader = get_autotrader()
    return trader.place_trade(pair, direction, entry, tp1, tp2, sl, units=units)
