with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    content = f.read()

# Relax the minute restriction
content = content.replace("and 10 <= ist_now.hour <= 15 and 0 <= ist_now.minute <= 5:", "and 10 <= ist_now.hour <= 15:")

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(content)
