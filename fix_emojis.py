with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("?? BTC Lottery Miner", "?? BTC Lottery Miner")
html = html.replace("?? Bitcoin Lottery Miner", "?? Bitcoin Lottery Miner")
html = html.replace("?? Start Solo Mining", "?? Start Solo Mining")
html = html.replace("? Time's up!", "? Time's up!")

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Emojis fixed!")
