from .base import BrokerBase
from .dummy import DummyBroker
from .delta import DeltaBroker
from .coinswitch import CoinswitchBroker
from .mt5 import MT5Broker

__all__ = ["BrokerBase", "DummyBroker", "DeltaBroker", "CoinswitchBroker", "MT5Broker"]


def get_broker(provider: str, **kwargs) -> BrokerBase:
    provider = (provider or "").lower()
    if provider in {"", "dummy"}:
        return DummyBroker(**kwargs)
    if provider in {"delta", "deltaexchange", "delta_exchange"}:
        return DeltaBroker(**kwargs)
    if provider in {"coinswitch", "coin-switch", "coinswitchpro"}:
        return CoinswitchBroker(**kwargs)
    if provider in {"mt5", "metatrader5", "meta5"}:
        return MT5Broker(**kwargs)
    # Unknown provider -> fall back to dummy
    return DummyBroker(**kwargs)
