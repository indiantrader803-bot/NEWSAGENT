with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('import asyncio\n                                asyncio.create_task(broadcast_message(bot, msg, parse_mode="HTML"))', 'await broadcast_message(bot, msg, parse_mode="HTML")')

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(content)
