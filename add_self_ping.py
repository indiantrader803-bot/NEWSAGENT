import re

with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    content = f.read()

ping_block = """
        # Keep-Alive Self Ping for Render Free Tier
        # This forces the Render router to see external traffic and prevents the web service from sleeping.
        if int(time.time()) % 600 < 60: # Every ~10 minutes
            try:
                import requests
                requests.get("https://newsagent-85h8.onrender.com/api/uptime", timeout=5)
            except:
                pass
"""

# Insert it in the main worker loop right after `await asyncio.sleep(60)`
# Actually, inside the `while True:` loop.
content = content.replace("        await asyncio.sleep(60)", "        await asyncio.sleep(60)\n" + ping_block)

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Self-ping added")
