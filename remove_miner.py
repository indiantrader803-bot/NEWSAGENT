import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove the Navigation Item
nav_pattern = r'<li class="nav-item" onclick="switchPage\(\'page-btc-lottery\', this\)">\s*?? BTC Lottery Miner\s*</li>'
html = re.sub(nav_pattern, '', html, flags=re.DOTALL)

# 2. Remove the HTML Page Panel
page_pattern = r'<!-- BTC LOTTERY MINER PAGE -->\s*<div id="page-btc-lottery" class="page-panel">.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*'
# Wait, my previous insertion of the page panel was:
# <!-- BTC LOTTERY MINER PAGE -->
# <div id="page-btc-lottery" class="page-panel"> ... </div>
# Let's write a safer regex or use string matching.
