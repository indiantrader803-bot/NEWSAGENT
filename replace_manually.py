import re
with open("dashboard.html", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Replace the heading
content = re.sub(r"<h2[^>]*>.*?AI Option Momentum Engine</h2>", '<h2 style="font-size: 1.5rem; font-weight: 800; letter-spacing: -0.03em;">?? AI Option Momentum Engine</h2>', content)

# Replace the nav item
content = re.sub(r"onclick=\"switchPage\('page-momentum', this\); initMomentumEngine\(\);\">\s*.*?\s*</li>", "onclick=\"switchPage('page-momentum', this); initMomentumEngine();\">\n                ?? Option Momentum AI\n            </li>", content)

# Replace Active trades
content = re.sub(r"<h3[^>]*>.*?Active Option Trades</h3>", '<h3 style="font-size: 1.1rem; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 0.5rem; margin-bottom: 1rem;">? Active Option Trades</h3>', content)

# Replace Event Log
content = re.sub(r"<h3[^>]*>.*?Event Log</h3>", '<h3 style="font-size: 1.1rem; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 0.5rem; margin-bottom: 1rem;">?? Event Log</h3>', content)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Replaced manually")
