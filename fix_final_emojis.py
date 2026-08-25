import re
with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('<span>?? Stop Mining</span>', '<span>?? Stop Mining</span>')
html = html.replace('?? BLOCK FOUND! ??', '?? BLOCK FOUND! ??')
html = html.replace('<span>?? Start Solo Mining</span>', '<span>?? Start Solo Mining</span>')
html = html.replace('?? Mining stopped.', '?? Mining stopped.')

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
