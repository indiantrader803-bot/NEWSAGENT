class BrokerAdapter:
    def login(self):
        """Authenticate with the broker API."""
        raise NotImplementedError

    def place_order(self, symbol, side, qty, order_type, price=0.0):
        """Place a new order."""
        raise NotImplementedError

    def modify_order(self, order_id, price):
        """Modify an existing order (e.g. update Stop Loss)."""
        raise NotImplementedError

    def exit_order(self, order_id):
        """Cancel or close an order."""
        raise NotImplementedError

    def get_positions(self):
        """Fetch active positions."""
        raise NotImplementedError

    def connect_websocket(self, on_tick_callback):
        """Stream live market data ticks."""
        raise NotImplementedError
