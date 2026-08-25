with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove Sidebar Nav Item
nav_item_1 = """            <li class="nav-item" onclick="switchPage('page-btc-lottery', this)">
                ?? BTC Lottery Miner
            </li>"""
nav_item_2 = """<li class="nav-item" onclick="switchPage('page-btc-lottery', this)">
                  ?? BTC Lottery Miner
              </li>"""
html = html.replace(nav_item_1, "")
html = html.replace(nav_item_2, "")
html = html.replace("""<li class="nav-item" onclick="switchPage('page-btc-lottery', this)">\n                ?? BTC Lottery Miner\n            </li>""", "")

# 2. Extract and remove the HTML panel
start_idx = html.find("<!-- BTC LOTTERY MINER PAGE -->")
if start_idx != -1:
    # Find the end of this div. It ends right before the closing of main-content.
    # The next thing after it is probably script tags or Chat Bot Integration or similar, or just end of workspace.
    # We can search for the start of the <script> block
    end_idx = html.find("<script>", start_idx)
    
    # We just want to remove up to the closing divs before script
    if end_idx != -1:
        # Actually, let's just find the precise block
        pass

    # A safer way:
    import re
    # Remove from <!-- BTC LOTTERY MINER PAGE --> to the end of the <div id="page-btc-lottery" ...>
    page_pattern = r'<!-- BTC LOTTERY MINER PAGE -->.*?<div id="page-btc-lottery" class="page-panel">.*?(?=\n\s*</main-content>|\n\s*</div>\s*</div>\s*</div>\s*<script>|\n\s*</div>\s*<script>|\n\s*</div>\s*</div>\s*<script>)'
    # The previous structure was that it was just appended. Let's just use regex to strip out the page panel.
