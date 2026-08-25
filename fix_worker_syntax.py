with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the broken nifty_msg literal newlines
import re
content = re.sub(
    r'nifty_msg = ".*?LIVE HOURLY NIFTY OPTION SETUP.*?" \+ ".*?".join\(nifty_lines\[:3\]\) \+ ".*?_Market internals suggest momentum in these zones._"',
    'nifty_msg = "?? *LIVE HOURLY NIFTY OPTION SETUP*\\n\\n" + "\\n".join(nifty_lines[:3]) + "\\n\\n_Market internals suggest momentum in these zones._"',
    content,
    flags=re.DOTALL
)

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(content)
