with open("smc_matrix.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        try:
            tk = yf.Ticker(sym)
            
            # Fetch multiple intervals
            # 15m (last 5 days)
            df_15m = tk.history(period="5d", interval="15m")"""

replacement = """        try:
            tk = yf.Ticker(sym)
            df_15m = tk.history(period="5d", interval="15m")
            
            if df_15m.empty and "." not in sym and "=" not in sym and "-" not in sym and "^" not in sym:
                sym = f"{sym}.NS"
                tk = yf.Ticker(sym)
                df_15m = tk.history(period="5d", interval="15m")
            
            # Fetch multiple intervals
            # 1h (last 1mo)"""

content = content.replace(target, replacement)

with open("smc_matrix.py", "w", encoding="utf-8") as f:
    f.write(content)

print("patched smc_matrix")
