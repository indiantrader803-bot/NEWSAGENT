with open("main.py", "r", encoding="utf-8") as f:
    main_content = f.read()

target = """                analysis = _analyzer_groq_chat(prompt, system_prompt="You are a senior macro trading strategist. Be concise, direct and data-driven.")
                response_body = json.dumps({"analysis": analysis})"""

fallback = """                analysis = _analyzer_groq_chat(prompt, system_prompt="You are a senior macro trading strategist. Be concise, direct and data-driven.")
                if not analysis:
                    if actual == "N/A" or not actual:
                        analysis = "Algorithmic Analysis: The market is currently awaiting the actual figures for this event. Institutional positions are likely hedged to prevent volatility exposure. Expect short-term spikes across relevant Forex and Index pairs upon release."
                    else:
                        analysis = f"Algorithmic Analysis: The actual figure of {actual} compared to the forecast of {forecast} creates a measurable deviation. If actual > forecast for inflation/jobs, expect currency strength and equity weakness. If actual < forecast, expect currency weakness and equity relief rallies."
                response_body = json.dumps({"analysis": analysis})"""

main_content = main_content.replace(target, fallback)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_content)

print("done calendar")
