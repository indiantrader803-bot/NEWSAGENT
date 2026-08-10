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


AUTOTRADE_ENABLED = os.getenv("AUTOTRADE_ENABLED", "").strip() in {"1", "true", "yes"}
BROKER_PROVIDER = os.getenv("BROKER_PROVIDER", "dummy").strip().lower()
AUTOTRADE_MODE = os.getenv("AUTOTRADE_MODE", "paper").strip().lower()
MAX_UNITS_PER_TRADE = float(os.getenv("MAX_UNITS_PER_TRADE", "0").strip() or 0)
_LEVERAGE_RAW = os.getenv("LEVERAGE", "1:1").strip()


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

    def place_trade(self, pair: str, direction: str, entry: float, tp1: float, tp2: float, sl: float, units: Optional[float] = None) -> dict:
        if not AUTOTRADE_ENABLED:
            return {"status": "disabled"}

        side = "buy" if direction.lower().startswith("buy") else "sell"
        # Default units: 1000 if unspecified (paper)
        units = float(units) if units else 1000.0

        # Enforce per-trade maximum if configured (0 => no limit)
        if MAX_UNITS_PER_TRADE and units > MAX_UNITS_PER_TRADE:
            return {"status": "rejected", "reason": f"units {units} exceed MAX_UNITS_PER_TRADE={MAX_UNITS_PER_TRADE}"}

        # Use primary target tp1 for attaching take profit/stop loss
        try:
            # include leverage in request so adapters can convert units->lots appropriately
            resp = self.broker.place_order(pair=pair, side=side, units=units, entry=entry, tp=tp1, sl=sl, leverage=LEVERAGE)
            return {"status": "ok", "order": resp}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}


_AUTOTRADER: AutoTrader | None = None


def get_autotrader() -> AutoTrader:
    global _AUTOTRADER
    if _AUTOTRADER is None:
        _AUTOTRADER = AutoTrader()
    return _AUTOTRADER


def place_trade(pair: str, direction: str, entry: float, tp1: float, tp2: float, sl: float, units: Optional[float] = None) -> dict:
    trader = get_autotrader()
    return trader.place_trade(pair, direction, entry, tp1, tp2, sl, units=units)
