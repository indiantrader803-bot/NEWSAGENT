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
