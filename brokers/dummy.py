from .base import BrokerBase
from typing import Dict, Any
import uuid
import time


class DummyBroker(BrokerBase):
    """A simple paper/simulated broker for testing autotrade flows.

    This adapter logs trades to a local file `autotrade_dummy.log` and returns
    a simulated order response. Use by setting BROKER_PROVIDER=dummy and
    AUTOTRADE_MODE=paper.
    """

    def __init__(self, logfile: str = "autotrade_dummy.log", **kwargs):
        super().__init__(**kwargs)
        self.logfile = logfile

    def place_order(self, pair: str, side: str, units: float, entry: float, tp: float, sl: float, **kwargs) -> Dict[str, Any]:
        order_id = str(uuid.uuid4())
        timestamp = int(time.time())
        resp = {
            "id": order_id,
            "status": "simulated",
            "pair": pair,
            "side": side,
            "units": units,
            "entry": entry,
            "tp": tp,
            "tp2": kwargs.get("tp2"),
            "sl": sl,
            "timestamp": timestamp,
            "leverage": kwargs.get("leverage"),
        }
        try:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(str(resp) + "\n")
        except Exception:
            pass
        return resp
