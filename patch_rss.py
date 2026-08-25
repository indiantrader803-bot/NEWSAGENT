with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """    LIVE_NEWS_FEEDS = [
        "https://feeds.feedburner.com/forexcom",
        "https://www.investing.com/rss/news_1.rss",
        "https://www.forexlive.com/Feed/News",
        "https://finance.yahoo.com/news/rss"
    ]"""

replacement = """    LIVE_NEWS_FEEDS = [
        "https://economictimes.indiatimes.com/markets/rssfeeds/2146842.cms",
        "https://www.livemint.com/rss/markets",
        "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "https://feeds.feedburner.com/forexcom",
        "https://www.investing.com/rss/news_1.rss",
        "https://www.forexlive.com/Feed/News",
        "https://finance.yahoo.com/news/rss"
    ]"""

content = content.replace(target, replacement)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("patched rss")
