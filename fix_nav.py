import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

target_nav = r"<li class=\"nav-item\" onclick=\"switchPage\('page-tools', this\)\">[\s\S]*?</li>"
replacement_nav = """            <li class="nav-item" onclick="switchPage('page-momentum', this); initMomentumEngine();">
                ?? Option Momentum AI
            </li>
            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>"""

content = re.sub(target_nav, replacement_nav, content)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Nav fixed")
