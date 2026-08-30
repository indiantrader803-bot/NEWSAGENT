with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    worker_content = f.read()

bad_string = """alert_msg = f"?? *SYSTEM ALERT*
Error detected in 24/7 Engine:
`{str(error_message)[:200]}`\""""
good_string = 'alert_msg = f"?? *SYSTEM ALERT*\\nError detected in 24/7 Engine:\\n`{str(error_message)[:200]}`"'

worker_content = worker_content.replace(bad_string, good_string)

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(worker_content)
    
with open("main.py", "r", encoding="utf-8") as f:
    main_content = f.read()
    
bad_main = """await send_telegram_message(bot, f"?? *API/CYCLE ERROR*
`{msg[:200]}`", parse_mode="Markdown")"""
good_main = 'await send_telegram_message(bot, f"?? *API/CYCLE ERROR*\\n`{msg[:200]}`", parse_mode="Markdown")'

main_content = main_content.replace(bad_main, good_main)
with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_content)

print("Syntax properly fixed")
