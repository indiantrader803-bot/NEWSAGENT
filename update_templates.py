import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace Forex/Crypto Trade Signal formatting block
forex_mod = """                  is_buy = (is_bullish == (multiplier > 0))
                  direction_label = "BUY" if is_buy else "SELL"
                  dir_icon  = "dYY BUY" if is_buy else "dY"' SELL"
                  e  = round(price, 4)
                  t1 = round(price + 75 * pip_size if is_buy else price - 75 * pip_size, 4)
                  t2 = round(price + 150 * pip_size if is_buy else price - 150 * pip_size, 4)
                  s  = round(price - 15 * pip_size if is_buy else price + 15 * pip_size, 4)
                  reward = abs(t2 - e)
                  risk   = abs(s - e)
                  rr_str = f"{reward / risk:.1f}" if risk > 0 else "?"
                  conf_pct = _confidence_pct(confidence)
                  ai_reason = _strip_md(ai_analyze_news(article) or title[:200])
                  inst_name = INSTRUMENT_NAMES.get(pair, pair)
                  log_signal(pair, direction_label, e, t1, t2, s, "forex")
                  
                  lines = [
                      f"dY' *FOREX & CRYPTO INTELLIGENCE* dY'",
                      f"dY"S *Pair:* {pair} ({inst_name})",
                      f"dY"- *Action:* {dir_icon} @ {_price_str(e, pair)}",
                      "dY dY dY dY dY dY dY dY dY dY dY dY dY dY ",
                      f"dY"O *Stop Loss (SL):*  {_price_str(s, pair)}",
                      f"dY OS *Target 1 (TP):*  {_price_str(t1, pair)}",
                      f"dYZ_ *Target 2 (TP):*  {_price_str(t2, pair)}",
                      "dY dY dY dY dY dY dY dY dY dY dY dY dY dY ",
                      f"s-,? *Risk/Reward:* 1:{rr_str}",
                      f"dY - *AI Confidence:* {conf_pct}%",
                      "",
                      f"dY"? *AI Thesis:* {ai_reason[:350]}",
                      "",
                      f"dY  *Trading Strategy:*",
                      f"a  *Beginner:* Use {_price_str(e, pair)} to enter. Keep SL tight at {_price_str(s, pair)}.",
                      f"a  *Pro:* Scale out 50% at TP1 ({_price_str(t1, pair)}), trail SL for TP2.",
                      "",
                      f"dY"- #{asset_sym} #Forex #Crypto {'#Long' if is_buy else '#Short'} #Signal",
                      f"s,? _Not financial advice._"
                  ]
                  if link:
                      lines.append(f"dY"S Source: {link}")
                  return "\\n".join(lines)"""
# Using regex to replace the block
content = re.sub(r'is_buy = \(is_bullish == \(multiplier > 0\)\).*?return "\\n"\.join\(lines\)', forex_mod, content, flags=re.DOTALL)

# Replace Indian Market Trade Signal formatting block
india_mod = """                  is_buy = direction_str == "Bullish"
                  direction_label = "BUY" if is_buy else "SELL"
                  dir_icon  = "dYY BUY (LONG)" if is_buy else "dY"' SELL (SHORT)"
                  e  = round(price, 2)
                  t1 = round(price + (price * 0.01) if is_buy else price - (price * 0.01), 2)
                  t2 = round(price + (price * 0.02) if is_buy else price - (price * 0.02), 2)
                  s  = round(price - (price * 0.005) if is_buy else price + (price * 0.005), 2)
                  reward = abs(t2 - e)
                  risk   = abs(s - e)
                  rr_str = f"{reward / risk:.1f}" if risk > 0 else "?"
                  conf_pct = _confidence_pct(confidence)
                  ai_reason = _strip_md(ai_analyze_news(article) or title[:200])
                  inst_name = INSTRUMENT_NAMES.get(asset, asset)
                  log_signal(asset, direction_label, e, t1, t2, s, "india")

                  lines = [
                      f"dYrdY3 *INDIAN MARKET SWING SETUP* dYrdY3",
                      f"dY"S *Asset:* {asset} ({inst_name})",
                      f"dY>- *Setup:* {dir_icon}",
                      ""?"?"?"?"?"?"?"?"?"?"?"?"?"?",
                      f"dY"O *Entry Price:*   ,1{e}",
                      f"dYZ_ *Take Profit 1:* ,1{t1} (+1%)",
                      f"dYZ_ *Take Profit 2:* ,1{t2} (+2%)",
                      f"dY>` *Stop Loss:*     ,1{s}  (-0.5%)",
                      ""?"?"?"?"?"?"?"?"?"?"?"?"?"?",
                      f"dY c *Structure:* 1:{rr_str} R:R | *AI:* {conf_pct}%",
                      "",
                      f"dY"? *Market Context:* {ai_reason[:300]}",
                      "",
                      f"dY"- #{asset} #NSE #IndianStockMarket {'#Bullish' if is_buy else '#Bearish'}",
                      f"s,? _Strict Risk Management Advised._"
                  ]
                  if link:
                      lines.append(f"dY"S Link: {link}")
                  return "\\n".join(lines)"""
content = re.sub(r'is_buy = direction_str == "Bullish"((?!def).)*?return "\\n"\.join\(lines\)', india_mod, content, flags=re.DOTALL)

# Replace Intraday Stock formatting block
intraday_mod = """                  is_buy = direction_str == "Bullish"
                  direction_label = "BUY" if is_buy else "SELL"
                  dir_icon  = "dYY INTRADAY LONG" if is_buy else "dY"' INTRADAY SHORT"
                  e  = round(price, 2)
                  t1 = round(price + (price * 0.005) if is_buy else price - (price * 0.005), 2)
                  t2 = round(price + (price * 0.01) if is_buy else price - (price * 0.01), 2)
                  s  = round(price - (price * 0.0025) if is_buy else price + (price * 0.0025), 2)
                  reward = abs(t2 - e)
                  risk   = abs(s - e)
                  rr_str = f"{reward / risk:.1f}" if risk > 0 else "?"
                  conf_pct = _confidence_pct(confidence)
                  ai_reason = _strip_md(ai_analyze_news(article) or title[:200])
                  inst_name = INSTRUMENT_NAMES.get(asset, asset)
                  log_signal(asset, direction_label, e, t1, t2, s, "intraday")

                  lines = [
                      f"aZ!i *INTRADAY SCALP ALERT* aZ!i",
                      f"dY"S *Stock:* {asset} ({inst_name})",
                      f"dY % *Direction:* {dir_icon}",
                      "? ? ? ? ? ? ? ? ? ? ? ?",
                      f"a  *Entry:* ,1{e}",
                      f"dY c *Target 1:* ,1{t1} (0.5%)",
                      f"dY c *Target 2:* ,1{t2} (1.0%)",
                      f"dY. *Stop Loss:* ,1{s} (0.25%)",
                      "? ? ? ? ? ? ? ? ? ? ? ?",
                      f"-,? *Momentum:* {conf_pct}% AI Score",
                      "",
                      f"dY"? *Catalyst:* {ai_reason[:200]}",
                      "",
                      f"dY"- #{asset} #Intraday #DayTrading {'#Long' if is_buy else '#Short'}",
                      f"s,? _Fast execution required._"
                  ]
                  if link:
                      lines.append(f"dY"S Link: {link}")
                  return "\\n".join(lines)"""
content = re.sub(r'is_buy = direction_str == "Bullish"((?!def).)*?return "\\n"\.join\(lines\)', intraday_mod, content, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
