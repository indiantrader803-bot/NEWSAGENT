from .base_adapter import BrokerAdapter

class DhanAdapter(BrokerAdapter):
    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token
        # In a real setup, initialize the DhanHQ client here

    def login(self):
        print(f"[Dhan] Logged in with client_id: {self.client_id}")
        return True

    def place_order(self, symbol, side, qty, order_type, price=0.0):
        print(f"[Dhan] Placing {side} order for {symbol}, Qty: {qty}")
        return {"orderId": "DHAN_" + str(int(price*100)), "status": "PENDING"}

    def modify_order(self, order_id, price):
        print(f"[Dhan] Modifying order {order_id} to price {price}")
        return True

    def exit_order(self, order_id):
        print(f"[Dhan] Exiting order {order_id}")
        return True

    def get_positions(self):
        return []

    def connect_websocket(self, on_tick_callback):
        print("[Dhan] Connecting to WebSocket (Simulated)")
        # In a real setup, connect to wss://api-feed.dhan.co
        pass
