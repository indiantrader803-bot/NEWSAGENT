import re
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

fallback_code = """    if not TWITTER_BEARER_TOKEN:
        try:
            import feedparser
            import urllib.parse
            query = urllib.parse.quote(TWITTER_SEARCH_QUERY + " site:twitter.com")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            results = []
            for entry in feed.entries[:5]:
                results.append({
                    "title": entry.title,
                    "description": entry.get("summary", ""),
                    "link": entry.link,
                    "pubDate": entry.get("published", ""),
                    "source_name": "Twitter",
                    "keywords": ["twitter", "social"],
                })
            return results
        except Exception as e:
            print(f"[ERROR] Twitter fallback failed: {e}")
            return []"""

content = re.sub(r'    if not TWITTER_BEARER_TOKEN:\n        return \[\]', fallback_code, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
