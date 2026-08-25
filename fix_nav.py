import re
with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

nav_str = r'(<li class="nav-item" onclick="switchPage\(\'page-tools\', this\)">.*?</li>)'
replacement = r'\1\n            <li class="nav-item" onclick="switchPage(\'page-btc-lottery\', this)">\n                ?? BTC Lottery Miner\n            </li>'

html = re.sub(nav_str, replacement, html, flags=re.DOTALL)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
