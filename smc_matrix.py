import yfinance as yf
import pandas as pd
import numpy as np

def identify_trend_and_fvg(df):
    """Basic logic to find trend and fair value gaps."""
    if len(df) < 5:
        return {"trend": "NEUTRAL", "bias": "Insufficient Data"}
    
    # Simple EMAs for trend
    close = df['Close']
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    
    last_close = close.iloc[-1]
    last_ema9 = ema9.iloc[-1]
    last_ema21 = ema21.iloc[-1]
    
    trend = "NEUTRAL"
    if last_close > last_ema9 > last_ema21:
        trend = "BULLISH"
    elif last_close < last_ema9 < last_ema21:
        trend = "BEARISH"
        
    # Check for FVG in last 3 candles
    # Bullish FVG: Low of candle 3 > High of candle 1
    # Bearish FVG: High of candle 3 < Low of candle 1
    bias = "Consolidating"
    fvg_found = None
    
    if len(df) >= 3:
        for i in range(-3, 0):
            if abs(i) <= len(df) - 2:
                # Need i-2, i-1, i
                try:
                    c1_high = df['High'].iloc[i-2]
                    c1_low = df['Low'].iloc[i-2]
                    c3_high = df['High'].iloc[i]
                    c3_low = df['Low'].iloc[i]
                    
                    if c3_low > c1_high:
                        fvg_found = ("BULLISH FVG", round((c3_low + c1_high)/2, 4))
                    elif c3_high < c1_low:
                        fvg_found = ("BEARISH FVG", round((c3_high + c1_low)/2, 4))
                except:
                    pass

    if trend == "BULLISH":
        bias = "Strong Uptrend" if fvg_found and fvg_found[0] == "BULLISH FVG" else "Uptrend"
    elif trend == "BEARISH":
        bias = "Strong Downtrend" if fvg_found and fvg_found[0] == "BEARISH FVG" else "Downtrend"
        
    return {
        "trend": trend,
        "bias": bias,
        "fvg": fvg_found
    }

def scan_smc(symbols_list):
    matrix = []
    setups = []
    
    for sym in symbols_list:
        sym = sym.strip()
        if not sym: continue
        
        try:
            tk = yf.Ticker(sym)
            df_15m = tk.history(period="5d", interval="15m")
            
            if df_15m.empty and "." not in sym and "=" not in sym and "-" not in sym and "^" not in sym:
                sym = f"{sym}.NS"
                tk = yf.Ticker(sym)
                df_15m = tk.history(period="5d", interval="15m")
            
            # Fetch multiple intervals
            # 1h (last 1mo)
            # 1h (last 1mo)
            df_1h = tk.history(period="1mo", interval="1h")
            # 1d (last 3mo)
            df_1d = tk.history(period="3mo", interval="1d")
            
            # We skip 4H because yfinance doesn't natively support 4h easily without resample or 730d limit logic that sometimes fails.
            # We'll approximate 4h by resampling 1h or just duplicate 1h/1d logic if unavailable.
            if len(df_1h) > 0:
                df_4h = df_1h.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
            else:
                df_4h = pd.DataFrame()

            res_15m = identify_trend_and_fvg(df_15m)
            res_1h = identify_trend_and_fvg(df_1h)
            res_4h = identify_trend_and_fvg(df_4h)
            res_1d = identify_trend_and_fvg(df_1d)
            
            # Calculate confluence score
            bull_points = 0
            bear_points = 0
            for r in [res_15m, res_1h, res_4h, res_1d]:
                if r['trend'] == 'BULLISH': bull_points += 25
                elif r['trend'] == 'BEARISH': bear_points += 25
                
            score = max(bull_points, bear_points)
            verdict = "Mixed/Neutral"
            if bull_points >= 75: verdict = "High Probability Long"
            elif bear_points >= 75: verdict = "High Probability Short"
            elif bull_points == 50 and bear_points == 0: verdict = "Leaning Bullish"
            elif bear_points == 50 and bull_points == 0: verdict = "Leaning Bearish"
            
            if bull_points >= bear_points:
                final_score = 50 + (bull_points / 2)
            else:
                final_score = 50 - (bear_points / 2)
                
            matrix.append({
                "symbol": sym,
                "t15m": res_15m,
                "t1h": res_1h,
                "t4h": res_4h,
                "t1d": res_1d,
                "score": int(final_score),
                "verdict": verdict
            })
            
            # Extract setups
            for timeframe, r in [("15M", res_15m), ("1H", res_1h), ("4H", res_4h), ("Daily", res_1d)]:
                if r.get('fvg'):
                    setup_type = "BULLISH" if "BULLISH" in r['fvg'][0] else "BEARISH"
                    setups.append({
                        "symbol": sym,
                        "setup_type": r['fvg'][0],
                        "type": setup_type,
                        "timeframe": timeframe,
                        "description": f"Imbalance detected. Price may gravitate towards the Fair Value Gap at this level before continuing its {r['trend'].lower()} structure.",
                        "level": f"{r['fvg'][1]}"
                    })
                    
        except Exception as e:
            print(f"Error scanning {sym}: {e}")
            
    return {"matrix": matrix, "setups": setups}
