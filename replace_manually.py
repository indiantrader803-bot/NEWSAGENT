with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

def replace_block(start_marker, end_marker, new_content):
    global lines
    start_idx = -1
    for i, line in enumerate(lines):
        if start_marker in line:
            start_idx = i
            break
            
    if start_idx == -1:
        print(f"Marker not found: {start_marker}")
        return
        
    end_idx = -1
    for i in range(start_idx, len(lines)):
        if end_marker in lines[i]:
            end_idx = i
            break
            
    if end_idx == -1:
        print(f"End Marker not found: {end_marker}")
        return
        
    # Replace lines[start_idx:end_idx+1]
    lines = lines[:start_idx] + [new_content + "\n"] + lines[end_idx+1:]
    print(f"Replaced block starting at {start_idx} to {end_idx}")

forex_new = """                  theme = _get_today_theme()
                  sep = _style_sep(theme)
                  lines = [
                      f"?? *FOREX & CRYPTO INTELLIGENCE* ??",
                      f"?? *Pair:* {pair} ({inst_name})",
                      f"? *Action:* {dir_icon} @ {_price_str(e, pair)}",
                      "--------------------------------------",
                      f"?? *Stop Loss (SL):*  {_price_str(s, pair)}",
                      f"?? *Target 1 (TP):*  {_price_str(t1, pair)}",
                      f"?? *Target 2 (TP):*  {_price_str(t2, pair)}",
                      "--------------------------------------",
                      f"?? *Risk/Reward:* 1:{rr_str}",
                      f"?? *AI Confidence:* {conf_pct}%",
                      "",
                      f"?? *AI Thesis:* {ai_reason[:350]}",
                      "",
                      f"?? *Trading Strategy:*",
                      f"?? *Beginner:* Use {_price_str(e, pair)} to enter. Keep SL tight at {_price_str(s, pair)}.",
                      f"?? *Pro:* Scale out 50% at TP1 ({_price_str(t1, pair)}), trail SL for TP2.",
                      "",
                      f"?? #{asset_sym} #Forex #Crypto #Signal",
                      f"?? _Not financial advice._"
                  ]
                  if link:
                      lines.append(f"?? Source: {link}")
                  return "\\n".join(lines)"""
replace_block('theme = _get_today_theme()', 'return "\\n".join(lines)', forex_new)

india_new = """                  lines = [
                      f"???? *INDIAN MARKET SWING SETUP* ????",
                      f"?? *Asset:* {asset} ({inst_name})",
                      f"?? *Setup:* {dir_icon}",
                      "????????????????????",
                      f"?? *Entry Price:*   ?{e}",
                      f"?? *Take Profit 1:* ?{t1} (+1%)",
                      f"?? *Take Profit 2:* ?{t2} (+2%)",
                      f"?? *Stop Loss:*     ?{s}  (-0.5%)",
                      "????????????????????",
                      f"?? *Structure:* 1:{rr_str} R:R | *AI:* {conf_pct}%",
                      "",
                      f"?? *Market Context:* {ai_reason[:300]}",
                      "",
                      f"?? #{asset} #NSE #IndianStockMarket",
                      f"?? _Strict Risk Management Advised._"
                  ]
                  if link:
                      lines.append(f"?? Link: {link}")
                  return "\\n".join(lines)"""
replace_block('                  lines = [', 'return "\\n".join(lines)', india_new)

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
