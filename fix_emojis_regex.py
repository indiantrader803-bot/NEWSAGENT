import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r"\?\? AI Option Momentum Engine", "?? AI Option Momentum Engine", content)
content = re.sub(r"\?\? Option Momentum AI", "?? Option Momentum AI", content)
content = re.sub(r"\? Active Option Trades", "? Active Option Trades", content)
content = re.sub(r"\?\? Event Log", "?? Event Log", content)
content = re.sub(r"style=\"grid-template-columns: 2fr 1fr; gap: 1.5rem;\"", 'style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; align-items: start;"', content)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Emojis and CSS fixed")
