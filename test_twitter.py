import requests
import json
from bs4 import BeautifulSoup

def fetch_tweets(username):
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if script:
            data = json.loads(script.string)
            try:
                entries = data["props"]["pageProps"]["timeline"]["entries"]
                for e in entries:
                    content = e.get("content", {}).get("tweet", {})
                    if content:
                        text = content.get("text")
                        created_at = content.get("created_at")
                        print(f"[{created_at}] {text[:100]}")
            except KeyError:
                print("Could not parse entries.")
    else:
        print("Failed:", res.status_code)

fetch_tweets("reuters")
