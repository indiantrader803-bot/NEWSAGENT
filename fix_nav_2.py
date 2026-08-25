with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("switchPage(\\\'page-btc-lottery\\\', this)", "switchPage('page-btc-lottery', this)")

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
