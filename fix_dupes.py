with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

bad_block = """                # Always mark as seen so we don't re-process weak news endlessly
                seen_keys.add(full_key)
                seen_keys.add(key)
                if title_key: seen_keys.add(title_key)"""

good_block = """                # Always mark as seen so we don't re-process weak news endlessly
                seen_keys.add(full_key)
                seen_keys.add(key)
                if title_key: seen_keys.add(title_key)
                save_seen_keys(seen_keys)"""

if bad_block in code and good_block not in code:
    code = code.replace(bad_block, good_block)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Fixed!")
else:
    print("Not found or already fixed")
