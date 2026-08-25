with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# PATCH 1: /api/analyze
target_analyze = """                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if hist.empty:
                    raise Exception(f"No price data found for symbol '{symbol}'")"""

replacement_analyze = """                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if hist.empty and "." not in symbol and "=" not in symbol and "-" not in symbol and "^" not in symbol:
                    symbol = f"{symbol}.NS"
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                if hist.empty:
                    raise Exception(f"No price data found for symbol '{symbol}'")"""

content = content.replace(target_analyze, replacement_analyze)

# PATCH 2: /api/deep-analyze
target_deep = """                import yfinance as yf
                tk = yf.Ticker(symbol)
                hist = tk.history(period="5d")
                if hist.empty:
                    raise Exception(f"No real market price data found for symbol '{symbol}' on Yahoo Finance. Please enter a valid ticker.")"""

replacement_deep = """                import yfinance as yf
                tk = yf.Ticker(symbol)
                hist = tk.history(period="5d")
                if hist.empty and "." not in symbol and "=" not in symbol and "-" not in symbol and "^" not in symbol:
                    symbol = f"{symbol}.NS"
                    tk = yf.Ticker(symbol)
                    hist = tk.history(period="5d")
                if hist.empty:
                    raise Exception(f"No real market price data found for symbol '{symbol}' on Yahoo Finance. Please enter a valid ticker.")"""

content = content.replace(target_deep, replacement_deep)

# PATCH 3: /api/finrobot-report
target_fin = """                import yfinance as yf
                tk = yf.Ticker(symbol)
                hist = tk.history(period="1y")
                if hist.empty:
                    raise Exception(f"No price data found for symbol '{symbol}' on Yahoo Finance.")"""

replacement_fin = """                import yfinance as yf
                tk = yf.Ticker(symbol)
                hist = tk.history(period="1y")
                if hist.empty and "." not in symbol and "=" not in symbol and "-" not in symbol and "^" not in symbol:
                    symbol = f"{symbol}.NS"
                    tk = yf.Ticker(symbol)
                    hist = tk.history(period="1y")
                if hist.empty:
                    raise Exception(f"No price data found for symbol '{symbol}' on Yahoo Finance.")"""

content = content.replace(target_fin, replacement_fin)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("patched yfinance")
