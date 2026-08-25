import re
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

fallback_code = """    if not TWITTER_BEARER_TOKEN:
        try:
            import urllib.parse
            query = urllib.parse.quote(TWITTER_SEARCH_QUERY + " site:twitter.com")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            articles = fetch_live_news_from_url(url)
            for a in articles:
                a["source_name"] = "Twitter"
            return articles[:10]
        except Exception as e:
            print(f"[ERROR] Twitter fallback failed: {e}")
            return []"""

content = re.sub(r'    if not TWITTER_BEARER_TOKEN:(.*?return \[\])', fallback_code, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
