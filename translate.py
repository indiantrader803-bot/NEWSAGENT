import ai_agent

def translate_to_bengali(text: str) -> str:
    prompt = f"Translate the following financial news into Bengali language concisely. Output ONLY the Bengali text, nothing else:\n\n{text}"
    return ai_agent._best_ai(prompt, system_prompt="You are a professional financial translator.")

print(translate_to_bengali('Trump announces new tariffs on China, causing a drop in Forex markets.'))
