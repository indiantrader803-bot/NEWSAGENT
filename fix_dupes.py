import re

# 1. Modify main.py
with open("main.py", "r", encoding="utf-8") as f:
    main_content = f.read()

main_content = main_content.replace(
"""async def send_category_article(
    bot: Bot,
    articles: list[dict[str, Any]],
    seen_keys: set[str],
    category_prefix: str,
    format_func: Any,
) -> int:""",
"""async def send_category_article(
    bot: Bot,
    articles: list[dict[str, Any]],
    seen_keys: set[str],
    category_prefix: str,
    format_func: Any,
    silent_init: bool = False,
) -> int:"""
)

silent_init_logic = """        # Deduplicate similar/repeated titles using word-order-invariant hashes
        title = article.get("title") or ""
        title_norm = clean_title_for_dedup(title)
        if title_norm:
            title_key = f"title:{title_norm}"
            if title_key in seen_keys:
                continue
                
        if silent_init:
            seen_keys.add(full_key)
            if title_norm:
                seen_keys.add(title_key)
            continue"""

main_content = re.sub(r'# Deduplicate similar/repeated titles using word-order-invariant hashes.*?if title_key in seen_keys:\s+continue', silent_init_logic, main_content, flags=re.DOTALL)

main_content = main_content.replace(
"""async def run_worker_cycle(bot: Bot, seen_keys: set[str]) -> int:""",
"""async def run_worker_cycle(bot: Bot, seen_keys: set[str], silent_init: bool = False) -> int:"""
)

main_content = main_content.replace(
"""        total_sent += await send_category_article(
            bot, forex_articles, seen_keys,
            "forex", format_forex_message,
        )""",
"""        total_sent += await send_category_article(
            bot, forex_articles, seen_keys,
            "forex", format_forex_message, silent_init
        )"""
)
main_content = main_content.replace(
"""        total_sent += await send_category_article(
            bot, india_articles, seen_keys,
            "india", format_india_message,
        )""",
"""        total_sent += await send_category_article(
            bot, india_articles, seen_keys,
            "india", format_india_message, silent_init
        )"""
)
main_content = main_content.replace(
"""        total_sent += await send_category_article(
            bot, intraday_articles, seen_keys,
            "intraday", format_intraday_message,
        )""",
"""        total_sent += await send_category_article(
            bot, intraday_articles, seen_keys,
            "intraday", format_intraday_message, silent_init
        )"""
)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_content)

# 2. Modify unified_24x7_worker.py
with open("unified_24x7_worker.py", "r", encoding="utf-8") as f:
    worker_content = f.read()

worker_content = worker_content.replace(
"""async def monitor_forex_signals(bot: Bot):
    \"\"\"Generate and send forex trading signals.\"\"\"
    category = "forex_signals"
    
    while True:
        try:
            sessions = get_current_market_session()
            
            if sessions["forex"] and state.can_send_message(category, FOREX_SIGNAL_INTERVAL):
                # Run main forex signal generation cycle
                seen_keys = main.load_seen_keys()
                sent = await main.run_worker_cycle(bot, seen_keys)
                main.save_seen_keys(seen_keys)
                
                if sent > 0:
                    state.record_message(category)
                    print(f"[FOREX] Sent {sent} signals")""",
"""is_forex_first_run = True

async def monitor_forex_signals(bot: Bot):
    \"\"\"Generate and send forex trading signals.\"\"\"
    global is_forex_first_run
    category = "forex_signals"
    
    while True:
        try:
            sessions = get_current_market_session()
            
            if sessions["forex"] and (is_forex_first_run or state.can_send_message(category, FOREX_SIGNAL_INTERVAL)):
                # Run main forex signal generation cycle
                seen_keys = main.load_seen_keys()
                sent = await main.run_worker_cycle(bot, seen_keys, silent_init=is_forex_first_run)
                main.save_seen_keys(seen_keys)
                
                if is_forex_first_run:
                    is_forex_first_run = False
                    print("[NEWS WORKER] Initial silent run complete. Old messages ignored.")
                elif sent > 0:
                    state.record_message(category)
                    print(f"[FOREX/NEWS] Sent {sent} signals")"""
)

with open("unified_24x7_worker.py", "w", encoding="utf-8") as f:
    f.write(worker_content)
