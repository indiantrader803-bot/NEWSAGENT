import re
with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'.. BTC Lottery Miner', '?? BTC Lottery Miner', html)
html = re.sub(r'.. Bitcoin Lottery Miner', '?? Bitcoin Lottery Miner', html)
html = re.sub(r'.. Start Solo Mining', '?? Start Solo Mining', html)
html = re.sub(r'.. Time\'s up!', '? Time\'s up!', html)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Regex Emojis fixed!")
