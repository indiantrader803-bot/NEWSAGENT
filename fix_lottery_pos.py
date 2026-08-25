import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Extract the BTC Lottery Page block
pattern = r'(<!-- BTC LOTTERY MINER PAGE -->.*?)(?=\s*<script>\n\s*let currentTab = \'ALL\';)'
match = re.search(pattern, html, re.DOTALL)
if not match:
    print("Could not find BTC Lottery block!")
    exit(1)

btc_block = match.group(1)

# Remove it from its current location
html = html.replace(btc_block, "")

# 2. Find the end of page-tools
# We know page-tools ends right before "    </div>\n    </div>" which closes main-content and workspace.
# Let's search for telegram-test-result and the closing divs.
tools_end_pattern = r'(<div id="telegram-test-result"[^>]*></div>\s*</div>\s*</div>\s*</div>\s*</div>)'

if not re.search(tools_end_pattern, html):
    print("Could not find end of page-tools!")
    exit(1)

# Insert btc_block right after the end of page-tools (i.e. inside main-content, before main-content closes)
html = re.sub(tools_end_pattern, r'\1\n\n' + btc_block, html)

# 3. Fix encoding of ?? emojis (replace with correct emojis)
html = html.replace("?? Bitcoin Lottery Miner", "?? Bitcoin Lottery Miner")
html = html.replace("?? Start Solo Mining", "?? Start Solo Mining")
html = html.replace("?? BTC Lottery Miner", "?? BTC Lottery Miner")

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Done!")
