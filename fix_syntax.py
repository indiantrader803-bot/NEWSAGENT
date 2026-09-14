with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Fix the broken multiline string
old_bad = 'f"?? *News:* _{news_summary}_\n\n"            f"*{asset}* | {icon}\\n\\n"'
new_good = 'f"?? *News:* _{news_summary}_\\n\\n"\n            f"*{asset}* | {icon}\\n\\n"'

code = code.replace("f\"?? *News:* _{news_summary}_\n\n\"            f\"*{asset}* | {icon}\\n\\n\"", new_good)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed syntax")
