with open("dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("?? AI Option Momentum", "?? AI Option Momentum")
content = content.replace("?? Option Momentum AI", "?? Option Momentum AI")
content = content.replace("? Active Option Trades", "? Active Option Trades")
content = content.replace("?? Event Log", "?? Event Log")

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Emojis forced")
