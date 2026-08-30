with open("main.py", "r", encoding="utf-8") as f:
    main_content = f.read()

main_content = main_content.replace('await send_telegram_message(bot, f"?? *API/CYCLE ERROR*\n`{msg[:200]}`", parse_mode="Markdown")', 'await send_telegram_message(bot, f"?? *API/CYCLE ERROR*\\n`{msg[:200]}`", parse_mode="Markdown")')

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_content)

with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    worker_content = f.read()

worker_content = worker_content.replace('alert_msg = f"?? *SYSTEM ALERT*\nError detected in 24/7 Engine:\n`{str(error_message)[:200]}`"', 'alert_msg = f"?? *SYSTEM ALERT*\\nError detected in 24/7 Engine:\\n`{str(error_message)[:200]}`"')

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(worker_content)
print("Syntax fixed")
