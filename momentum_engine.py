import time
import pandas as pd
from datetime import datetime
from momentum_db import log_strategy_event
import threading

class OptionMomentumEngine:
    def __init__(self, broker_adapter=None):
        self.broker = broker_adapter
        self.active = False
        self.ticks = [] # Raw ticks
        self.candles = pd.DataFrame()
        self.active_trades = {}
        
    def start(self):
        self.active = True
        log_strategy_event("SYSTEM", "START", "Momentum Engine Started")
        print("[Engine] Engine started")
        
        # Start simulated ticker thread if no real broker provided
        if not self.broker:
            threading.Thread(target=self._simulate_ticks, daemon=True).start()
            
    def stop(self):
        self.active = False
        log_strategy_event("SYSTEM", "STOP", "Momentum Engine Stopped")
        print("[Engine] Engine stopped")
        
    def _simulate_ticks(self):
        """Simulate incoming ticks to build candles (for paper trading/demo)"""
        import random
        price = 100.0
        symbol = "NIFTY_24200_CE"
        while self.active:
            price += random.uniform(-1, 1.2) # Slight bullish bias
            self.on_tick(symbol, price, random.randint(10, 100))
            time.sleep(1) # 1 tick per second
            
    def on_tick(self, symbol, price, volume):
        """Receive a live tick from the broker WebSocket"""
        now = datetime.utcnow()
        self.ticks.append({
            "symbol": symbol,
            "timestamp": now,
            "price": price,
            "volume": volume
        })
        
        # Every 5 seconds, aggregate for the sake of fast simulation (Normally 5 minutes)
        # We will use 5 seconds here to simulate the '5-minute' candle speed for the UI
        if len(self.ticks) >= 5:
            self._build_candle(symbol)
            
    def _build_candle(self, symbol):
        df = pd.DataFrame(self.ticks)
        if df.empty: return
        
        # Build OHLC
        _open = df.iloc[0]["price"]
        _high = df["price"].max()
        _low = df["price"].min()
        _close = df.iloc[-1]["price"]
        _volume = df["volume"].sum()
        
        new_candle = pd.DataFrame([{
            "timestamp": datetime.utcnow(),
            "open": _open,
            "high": _high,
            "low": _low,
            "close": _close,
            "volume": _volume
        }])
        
        self.candles = pd.concat([self.candles, new_candle], ignore_index=True)
        self.ticks = [] # Reset ticks for next candle
        
        self._analyze_structure(symbol)
        
    def _analyze_structure(self, symbol):
        """Implement the HL/LH and breakout detection"""
        if len(self.candles) < 6: return # Need at least 5 candles for average volume
        
        recent = self.candles.iloc[-5:]
        avg_vol = recent["volume"].mean()
        latest = self.candles.iloc[-1]
        
        # Simplify structure detection for prototype:
        # CE BUY: Close > High of previous candle, Volume > Avg
        # (Real implementation involves finding true swing highs/lows)
        
        prev = self.candles.iloc[-2]
        if latest["close"] > prev["high"] and latest["volume"] > avg_vol:
            # BUY SIGNAL DETECTED
            log_strategy_event(symbol, "SIGNAL", f"Breakout detected. Close: {latest['close']:.2f}, Vol: {latest['volume']}")
            self._execute_trade(symbol, "BUY", latest["close"])
            
        # Trailing SL Exit Logic
        if symbol in self.active_trades:
            trade = self.active_trades[symbol]
            if latest["close"] < trade["sl"]:
                log_strategy_event(symbol, "EXIT", f"Trailing SL hit at {latest['close']:.2f}")
                self._exit_trade(symbol, latest["close"])
            elif latest["close"] > trade["highest"]:
                trade["highest"] = latest["close"]
                # Move SL up (Trailing)
                new_sl = trade["highest"] * 0.95 # 5% trailing SL for CE
                if new_sl > trade["sl"]:
                    trade["sl"] = new_sl
                    log_strategy_event(symbol, "TRAIL", f"Moved SL to {new_sl:.2f}")

    def _execute_trade(self, symbol, side, price):
        if symbol in self.active_trades: return # Already in trade
        
        trade = {
            "symbol": symbol,
            "side": side,
            "entry": price,
            "highest": price,
            "sl": price * 0.9, # Initial 10% SL
            "status": "RUNNING"
        }
        self.active_trades[symbol] = trade
        log_strategy_event(symbol, "EXECUTE", f"Placed {side} order at {price:.2f}")
        
    def _exit_trade(self, symbol, price):
        if symbol in self.active_trades:
            trade = self.active_trades.pop(symbol)
            pnl = ((price - trade["entry"]) / trade["entry"]) * 100
            log_strategy_event(symbol, "CLOSED", f"Trade closed. P&L: {pnl:.2f}%")

engine = OptionMomentumEngine()
