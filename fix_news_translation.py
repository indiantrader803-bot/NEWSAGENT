import re

with open("requirements.txt", "a") as f:
    f.write("\ndeep-translator==1.11.4\n")

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Update Twitter Search Query to include Trump
content = re.sub(
    r'TWITTER_SEARCH_QUERY = os\.getenv\("TWITTER_SEARCH_QUERY", ".*?"\)\.strip\(\)',
    r'TWITTER_SEARCH_QUERY = os.getenv("TWITTER_SEARCH_QUERY", "trump OR forex OR crypto OR stocks OR nse site:twitter.com").strip()',
    content
)

# Insert the deep-translator logic and modify format_forex_message / format_india_message
translation_helper = """
def _translate_to_bengali(text: str) -> str:
    if not text:
        return ""
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='auto', target='bn').translate(text)
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return text

"""

# Insert translation helper before format_forex_message
content = content.replace("def format_forex_message(", translation_helper + "def format_forex_message(")

# Modify format_forex_message for Twitter news
forex_msg_mod = """
    # For Twitter news, translate description to Bengali
    if source.lower() == "twitter":
        desc = article.get("description", "")
        if desc:
            bengali_desc = _translate_to_bengali(desc)
            text_body = bengali_desc + "\n\n(Original: " + desc + ")"
            article["description"] = text_body  # Update for the rest of the flow
"""

# Modify format_india_message for Bengali translation
india_msg_mod = """
    # Translate Indian news description to Bengali
    desc = article.get("description", "")
    if desc:
        bengali_desc = _translate_to_bengali(desc)
        article["description"] = bengali_desc + "\n\n(Original: " + desc + ")"
"""

# We'll just patch the format functions directly
def patch_function(content, func_name, patch_code):
    pattern = r'(def ' + func_name + r'\(article: dict\[str, Any\]\) -> str:.*?)(    title     = _strip_md)'
    return re.sub(pattern, r'\1' + patch_code + r'\n\2', content, flags=re.DOTALL)

content = patch_function(content, 'format_forex_message', forex_msg_mod)
content = patch_function(content, 'format_india_message', india_msg_mod)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
