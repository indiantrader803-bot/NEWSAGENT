import re
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = """def fetch_twitter_posts() -> list[dict[str, Any]]:
    results = []
    if TWITTER_BEARER_TOKEN:
        try:
            import requests
            headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
            if TWITTER_USERNAMES:
                for username in TWITTER_USERNAMES:
                    user_resp = requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers=headers, timeout=5)
                    if user_resp.status_code == 200:
                        user_id = user_resp.json().get("data", {}).get("id")
                        if user_id:
                            tweets_resp = requests.get(f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at", headers=headers, timeout=5)
                            if tweets_resp.status_code == 200:
                                for tweet in tweets_resp.json().get("data", []):
                                    text = tweet.get("text") or ""
                                    if text:
                                        results.append({
                                            "title": text, "description": "",
                                            "link": f"https://x.com/{username}/status/{tweet.get('id')}",
                                            "pubDate": tweet.get("created_at", ""),
                                            "source_name": username, "keywords": [],
                                        })
            elif TWITTER_SEARCH_QUERY:
                search_resp = requests.get(f"https://api.twitter.com/2/tweets/search/recent?q={TWITTER_SEARCH_QUERY}&max_results=5&tweet.fields=created_at", headers=headers, timeout=5)
                if search_resp.status_code == 200:
                    for tweet in search_resp.json().get("data", []):
                        text = tweet.get("text") or ""
                        if text:
                            results.append({
                                "title": text, "description": "",
                                "link": f"https://x.com/i/web/status/{tweet.get('id')}",
                                "pubDate": tweet.get("created_at", ""),
                                "source_name": "Twitter", "keywords": [],
                            })
        except Exception as e:
            print(f"[ERROR] Twitter API failed: {e}")

    # Fallback if API fails or returns 0 results
    if not results:
        try:
            import urllib.parse
            q = TWITTER_SEARCH_QUERY
            if "site:twitter.com" not in q:
                q += " site:twitter.com"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-US&gl=US&ceid=US:en"
            articles = fetch_live_news_from_url(url)
            for a in articles:
                a["source_name"] = "Twitter"
            results.extend(articles[:10])
        except Exception as e:
            print(f"[ERROR] Twitter fallback failed: {e}")
            
    return results"""

# Replace the entire function
content = re.sub(r'def fetch_twitter_posts\(\) -> list\[dict\[str, Any\]\]:.*?return results', new_func, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
