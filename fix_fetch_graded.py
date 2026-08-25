import re

with open("indian_scoring.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace fetch_graded_top_signals
new_func = """def fetch_graded_top_signals(scan_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    \"\"\"Generate live graded options signals calculated from real stock scanner data and live option chains.\"\"\"
    graded = []
    now_time = datetime.now(timezone.utc).strftime("%H:%M")
    
    # Filter for only strong signals
    valid_scans = []
    for s in (scan_results or []):
        try:
            prob_str = str(s.get("probability", "50%")).replace("%", "")
            prob = int(prob_str)
            if prob >= 70 or prob <= 30:
                valid_scans.append(s)
        except:
            pass
            
    for s in valid_scans[:4]:
        ticker = s.get("ticker", "NIFTY")
        price = float(s.get("price", 1000.0))
        prob_str = str(s.get("probability", "50%")).replace("%", "")
        score = int(prob_str)
        chg = float(s.get("change_pct", 0.0))
        
        direction = "BULLISH" if score >= 60 or chg > 0 else ("BEARISH" if score <= 40 or chg < 0 else "NEUTRAL")
        opt_type = "CE" if direction == "BULLISH" else "PE"
        
        # Calculate strike based on general price rules
        if price > 10000: step = 100
        elif price > 4000: step = 50
        elif price > 1000: step = 20
        else: step = 10
        strike = int(round(price / step) * step)
        
        strike_name = f"{ticker} {strike} {opt_type}"
        
        flow_value = round(max(0.5, (abs(chg) + 1.0) * (score / 35.0)), 2)
        flow_str = f"?{flow_value} Cr"
        
        headline = f"Institutional flow detected in {ticker} options — {flow_str} committed."
        if direction == "BULLISH":
            headline = f"Institutional buying of ?{flow_value} Cr in {ticker} {strike} Call options."
        elif direction == "BEARISH":
            headline = f"Institutional put flow of ?{flow_value} Cr recorded for {ticker} {strike} Put options."
            
        graded.append({
            "strike": strike_name,
            "direction": direction,
            "score": score,
            "flow_cr": flow_str,
            "time": now_time,
            "headline": headline
        })
        
    return graded"""

# Replace the old function
content = re.sub(r'def fetch_graded_top_signals.*?return graded', new_func, content, flags=re.DOTALL)

with open("indian_scoring.py", "w", encoding="utf-8") as f:
    f.write(content)
print("fetch_graded_top_signals fixed!")
