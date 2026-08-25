with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("bengali_desc + \"\n\n(Original: \" + desc + \")\"", "bengali_desc + \"\\n\\n(Original: \" + desc + \")\"")
content = content.replace("bengali_desc + \"\n  \n  (Original: \" + desc + \")\"", "bengali_desc + \"\\n\\n(Original: \" + desc + \")\"")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
