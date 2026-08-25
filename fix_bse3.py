with open("main.py", "r", encoding="utf-8") as f:
    main_content = f.read()

# in main.py, look for `/api/broadcast-nifty-sensex-oi`
sensex_text_block = """            sensex_lines = []
            for s in report.get("sensex_oi", []):
                sensex_lines.append(f"?? <b>{s['strike']}</b> ({s['expiry']}) ? <b>{s['oi_change']}</b> [{s['sentiment']}]")
            sensex_text = "\\n".join(sensex_lines) if sensex_lines else "No active Sensex OI buildup."
"""
sensex_text_block_actual = """            sensex_lines = []
            for s in report.get("sensex_oi", []):
                sensex_lines.append(f"?? <b>{s['strike']}</b> ({s['expiry']}) ? <b>{s['oi_change']}</b> [{s['sentiment']}]")
            sensex_text = "\\n".join(sensex_lines) if sensex_lines else "No active Sensex OI buildup."
"""
# Let's just do a regex replace or string replace.
import re
sensex_match = re.search(r'sensex_text = "\\n"\.join\(sensex_lines\) if sensex_lines else "No active Sensex OI buildup."', main_content)

if sensex_match:
    bankex_inject = """
            bankex_lines = []
            for s in report.get("bankex_oi", []):
                bankex_lines.append(f"?? <b>{s['strike']}</b> ({s['expiry']}) ? <b>{s['oi_change']}</b> [{s['sentiment']}]")
            bankex_text = "\\n".join(bankex_lines) if bankex_lines else "No active Bankex OI buildup."
"""
    main_content = main_content[:sensex_match.end()] + "\n" + bankex_inject + main_content[sensex_match.end():]
    
    # Also update the message text
    msg_match = re.search(r'f"?? <b>SENSEX OI HIGHLIGHTS</b>\\n"[\s\n]*f"\{sensex_text\}\\n"', main_content)
    if msg_match:
        bankex_msg_inject = """f"?? <b>SENSEX OI HIGHLIGHTS</b>\\n"
                f"{sensex_text}\\n"
                f"?? <b>BANKEX OI HIGHLIGHTS</b>\\n"
                f"{bankex_text}\\n"
"""
        # wait, let's just replace the exact text
        main_content = re.sub(r'f"?? <b>SENSEX OI HIGHLIGHTS</b>\\n"\s*f"\{sensex_text\}\\n"', 'f"?? <b>SENSEX & BANKEX (BSE) OI HIGHLIGHTS</b>\\n"\n                f"{sensex_text}\\n"\n                f"{bankex_text}\\n"', main_content)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_content)

# Now in unified_24x7_worker.py
with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    uni_content = f.read()

# finding the intraday hourly scan
flag_text_match = re.search(r'sensex_str = "\\n"\.join\(\[f"?? \{s\[\'strike\'\]\} \(\{s\[\'oi_change\'\]\}\)" for s in report\.get\("sensex_oi", \[\]\)\]\)', uni_content)
if flag_text_match:
    bankex_uni_inject = """
                          bankex_str = "\\n".join([f"?? {s['strike']} ({s['oi_change']})" for s in report.get("bankex_oi", [])])"""
    uni_content = uni_content[:flag_text_match.end()] + bankex_uni_inject + uni_content[flag_text_match.end():]
    
    uni_content = uni_content.replace('f"{sensex_str}\\n\\n"', 'f"{sensex_str}\\n\\n"\n                              f"<b>[BSE] BANKEX OI BUILDUP:</b>\\n"\n                              f"{bankex_str}\\n\\n"')

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(uni_content)

print("Added bankex rendering")
