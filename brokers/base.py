from abc import ABC, abstractmethod
from typing import Any, Dict


class BrokerBase(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def place_order(self, pair: str, side: str, units: float, entry: float, tp: float, sl: float, **kwargs) -> Dict[str, Any]:
        """Place an order and return a dict with order details (id, status, filled_price, etc.).

        side: 'buy' or 'sell'
        units: positive number representing base units (or contracts)
        entry: requested entry price (for market orders this may be ignored)
        tp: take profit price
        sl: stop loss price
        """
        raise NotImplementedError()

    def get_order_status(self, order: dict) -> Dict[str, Any]:
        """Return current status for a given order record.

        Default implementation should be overridden by live adapters. It accepts
        the stored `order` dict (as written to trades file) and returns a dict
        with at least `id` and `status` keys. Example statuses: simulated, pending,
        partial, filled, canceled, closed.
        """
        return {"id": order.get("id"), "status": order.get("status", "simulated")}
