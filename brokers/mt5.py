from .base import BrokerBase
from typing import Dict, Any
import uuid
import time
import os

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except Exception:
    mt5 = None
    MT5_AVAILABLE = False


class MT5Broker(BrokerBase):
    """MetaTrader5 adapter. If the `MetaTrader5` package is installed and an
    MT5 terminal is running and configured, this adapter will attempt to
    submit orders. Otherwise it falls back to simulated logging to
    `autotrade_mt5.log`.
    """

    def __init__(self, logfile: str = "autotrade_mt5.log", **kwargs):
        super().__init__(**kwargs)
        self.logfile = logfile
        self.account = os.getenv("MT5_ACCOUNT", "").strip()

    def place_order(self, pair: str, side: str, units: float, entry: float, tp: float, sl: float, **kwargs) -> Dict[str, Any]:
        timestamp = int(time.time())
        order_id = str(uuid.uuid4())
        if MT5_AVAILABLE:
            try:
                # Minimal best-effort attempt; user should configure symbol and terminal
                lot = float(units) / 1000.0 if units else 0.1
                symbol = pair.replace("/", "")
                order_type = mt5.ORDER_TYPE_BUY if side.lower().startswith("buy") else mt5.ORDER_TYPE_SELL
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot,
                    "type": order_type,
                    "price": entry,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 20,
                    "magic": 234000,
                    "comment": "autotrade",
                }
                result = mt5.order_send(request)
                return {"provider": "mt5", "status": "sent", "result": result}
            except Exception as exc:
                # Fall through to simulated logging below
                pass

        resp = {
            "id": order_id,
            "provider": "mt5",
            "status": "simulated",
            "pair": pair,
            "side": side,
            "units": units,
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "timestamp": timestamp,
            "leverage": kwargs.get("leverage"),
            "mt5_available": MT5_AVAILABLE,
        }
        try:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(str(resp) + "\n")
        except Exception:
            pass
        return resp
