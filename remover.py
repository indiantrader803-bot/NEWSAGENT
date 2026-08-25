import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove nav item
nav_pattern = r'\s*<li class="nav-item" onclick="switchPage\(\'page-btc-lottery\', this\)">\s*.*?BTC Lottery Miner\s*</li>'
html = re.sub(nav_pattern, '', html)

# 2. Remove HTML panel
panel_pattern = r'\s*<!-- BTC LOTTERY MINER PAGE -->\s*<div id="page-btc-lottery" class="page-panel">.*?(?=\s*</div>\s*</div>\s*</div>\s*<script>|\s*</div>\s*</div>\s*<script>|\s*</div>\s*<script>)'
# Since it's inside main-content, it ends right before the closing divs of the workspace.
# Let's do a more robust approach: Find <!-- BTC LOTTERY MINER PAGE --> and then count </div> until balanced? 
# Actually, the page-panel div has no nested unclosed divs. We can just use a non-greedy match to the final "</div>" before the script tag.
panel_pattern2 = r'\s*<!-- BTC LOTTERY MINER PAGE -->\s*<div id="page-btc-lottery" class="page-panel">.*?(?=\s*<script>)'
# Wait, if we match up to <script>, we'll swallow the closing </div> of main-content and workspace.
