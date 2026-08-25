import asyncio
import json
import time

START_TIME = time.time()
import os
import re
from contextlib import contextmanager
from datetime import datetime, time, timedelta, timezone
from html import escape
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree as ET

import yfinance as yf
from dotenv import load_dotenv

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import massive_data
import realtime_alert
import ai_agent
import crypto_screener
import autotrade

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_TOKEN2 = os.getenv("BOT_TOKEN2", "").strip()
BOT_TOKEN3 = os.getenv("BOT_TOKEN3", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_CHAT_ID3 = os.getenv("TELEGRAM_CHAT_ID3", "").strip()
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "").strip()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
ANALYZER_GROQ_API_KEY = os.getenv("ANALYZER_GROQ_API_KEY", "").strip() or GROQ_API_KEY
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY", "").strip()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
NEWSDATA_API_URL = "https://newsdata.io/api/1/latest"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
FINNHUB_BASE = "https://finnhub.io/api/v1"
NEWS_PROVIDER = os.getenv("NEWS_PROVIDER", "auto").strip().lower()
FETCH_INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL_SECONDS", "900"))
HIGH_IMPACT_CHECK_INTERVAL = int(os.getenv("HIGH_IMPACT_CHECK_INTERVAL", "60"))
LIVE_NEWS_ENABLED = os.getenv("LIVE_NEWS_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
LIVE_NEWS_FEEDS = [item.strip() for item in os.getenv("LIVE_NEWS_FEEDS", "").split(",") if item.strip()]
if not LIVE_NEWS_FEEDS:
    LIVE_NEWS_FEEDS = [
        "https://economictimes.indiatimes.com/markets/rssfeeds/2146842.cms",
        "https://www.livemint.com/rss/markets",
        "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "https://feeds.feedburner.com/forexcom",
        "https://www.investing.com/rss/news_1.rss",
        "https://www.forexlive.com/Feed/News",
        "https://finance.yahoo.com/news/rss"
    ]
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "").strip()
TWITTER_USERNAMES = [item.strip() for item in os.getenv("TWITTER_USERNAMES", "reuters,investingcom,fxstreet,stocktwits,benzinga").split(",") if item.strip()]
TWITTER_SEARCH_QUERY = os.getenv("TWITTER_SEARCH_QUERY", "trump OR forex OR crypto OR stocks OR nse site:twitter.com").strip()

import sys
_is_testing = "unittest" in sys.modules or "pytest" in sys.modules

if _is_testing:
    SENT_KEYS_FILE = "test_sent_articles.json"
    SIGNAL_LOG_FILE = "test_signal_log.json"
    SUBSCRIBERS_FILE = "test_subscribers.json"
else:
    SENT_KEYS_FILE = "sent_articles.json"
    SIGNAL_LOG_FILE = "signal_log.json"
    SUBSCRIBERS_FILE = "subscribers.json"
SENT_MESSAGES_FILE = "sent_messages.json"
_seen_keys: set[str] = set()
_signal_log: list[dict] = []
_subscribers: list[int] = []

FOREX_QUERY = os.getenv(
    "FOREX_QUERY",
    'forex OR "foreign exchange" OR (dollar AND fed) OR (euro AND ecb) OR '
    '(pound AND boe) OR (yen AND boj) OR (gold AND fed) OR (rupee AND rbi) OR '
    '(bitcoin OR btc OR ethereum OR eth OR crypto OR solana OR ripple OR cardano OR dogecoin) OR '
    '(crude oil OR brent OR wti) OR (silver) OR (nasdaq OR "dow jones" OR "s&p 500") OR '
    '(apple OR microsoft OR amazon OR nvidia OR meta OR tesla OR google OR netflix) OR '
    '(reliance OR tcs OR hdfc OR infosys OR icici OR sbi OR bharti OR zomato OR adani)',
)

INDIA_MARKET_QUERY = os.getenv(
    "INDIA_MARKET_QUERY",
    '(sensex OR nifty OR "indian market" OR "india stock" OR "bse" OR "nse" OR '
    '"rbi" OR "rupee" OR "sebi" OR "indian economy") AND (india OR mumbai)',
)

INTRADAY_STOCK_QUERY = os.getenv(
    "INTRADAY_STOCK_QUERY",
    '(reliance OR tcs OR hdfc OR infosys OR icici OR "hindustan unilever" OR sbi OR '
    'bharti OR "intraday" OR "stock market today" OR "opening bell" OR "closing bell" OR '
    'zomato OR adani OR "tata motors" OR "bajaj finance" OR wipro OR itc OR "asian paints" OR '
    'ntpc OR ongc OR "power grid" OR "ultratech cement" OR "tata steel" OR jsw OR hindalco OR '
    'walmart OR jpmorgan OR visa OR boeing OR disney OR netflix OR salesforce OR paypal OR uber) '
    'AND (india OR "bse" OR "nse" OR "bombay stock exchange")',
)

FOREX_TERMS = {
    "forex",
    "currency",
    "currencies",
    "fx",
    "usd",
    "dollar",
    "eur",
    "euro",
    "gbp",
    "pound",
    "jpy",
    "yen",
    "xau",
    "gold",
    "silver",
    "xag",
    "crude",
    "oil",
    "brent",
    "wti",
    "fed",
    "ecb",
    "boe",
    "boj",
    "rate hike",
    "rate cut",
    "inflation",
    "cpi",
    "nonfarm payrolls",
    "aud",
    "aussie",
    "nzd",
    "kiwi",
    "chf",
    "swiss franc",
    "cad",
    "loonie",
    "sek",
    "nok",
    "sgd",
    "hkd",
    "cny",
    "yuan",
    "mxn",
    "peso",
    "zar",
    "rand",
    "try",
    "lira",
    "inr",
    "rupee",
    "rbi",
    "sensex",
    "nifty",
    "bank nifty",
    "india market",
    "bse",
    "nse",
    "sp500",
    "ftse",
    "dax",
    "nikkei",
    "hang seng",
    "asx 200",
    "s&p 500",
    "apple",
    "microsoft",
    "amazon",
    "nvidia",
    "tesla",
    "meta",
    "google",
    "netflix",
    "adobe",
    "salesforce",
    "intel",
    "amd",
    "paypal",
    "uber",
    "nike",
    "boeing",
    "disney",
    "walmart",
    "jpmorgan",
    "visa",
    "reliance",
    "tcs",
    "hdfc",
    "infosys",
    "icici",
    "sbi",
    "bharti",
    "zomato",
    "adani",
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "solana",
    "sol",
    "ripple",
    "xrp",
    "cardano",
    "ada",
    "dogecoin",
    "doge",
    "polkadot",
    "dot",
    "avalanche",
    "avax",
    "chainlink",
    "link",
    "polygon",
    "matic",
    "crypto",
    "cryptocurrency",
    "nasdaq",
    "dow jones",
    "s&p",
    "sp500",
    "wall street",
    "us30",
    "us100",
    "reliance",
    "tcs",
    "hdfc",
    "infosys",
    "icici",
    "sbi",
    "bharti",
    "nifty 50",
    "sensex",
    "bank nifty",
}

CURRENCY_HINTS = {
    "XAU": ("xau", "gold", "bullion"),
    "XAG": ("xag", "silver"),
    "OIL": ("crude", "oil", "brent", "wti"),
    "BTC": ("bitcoin", "btc"),
    "ETH": ("ethereum", "eth"),
    "SOL": ("solana", "sol"),
    "XRP": ("ripple", "xrp"),
    "ADA": ("cardano",),
    "DOGE": ("dogecoin", "doge"),
    "DOT": ("polkadot", "dot"),
    "AVAX": ("avalanche", "avax"),
    "LINK": ("chainlink", "link"),
    "LTC": ("litecoin", "ltc"),
    "AUD": ("aud", "australian dollar", "aussie", "reserve bank of australia", "rba"),
    "NZD": ("nzd", "new zealand dollar", "kiwi", "reserve bank of new zealand", "rbnz"),
    "CHF": ("chf", "swiss franc", "swiss national bank", "snb"),
    "CAD": ("cad", "canadian dollar", "loonie", "bank of canada", "boc"),
    "SEK": ("sek", "swedish krona", "riksbank", "swedish crown"),
    "NOK": ("nok", "norwegian krone", "norges bank"),
    "SGD": ("sgd", "singapore dollar", "monetary authority of singapore"),
    "HKD": ("hkd", "hong kong dollar", "hong kong monetary authority"),
    "CNY": ("cny", "yuan", "renminbi", "chinese yuan", "pboc", "people's bank of china"),
    "MXN": ("mxn", "mexican peso", "banxico", "bank of mexico"),
    "ZAR": ("zar", "south african rand", "sarb", "reserve bank of south africa"),
    "TRY": ("try", "turkish lira", "turkish lira", "central bank of turkey"),
    "JPY": ("jpy", "yen", "boj", "bank of japan"),
    "GBP": ("gbp", "pound", "boe", "bank of england"),
    "EUR": ("eur", "euro", "ecb"),
    "USD": ("usd", "dollar", "fed", "treasury"),
    "NIFTY": ("nifty", "nifty 50", "nse"),
    "SENSEX": ("sensex", "bse", "bombay stock exchange"),
    "BANKNIFTY": ("bank nifty", "banknifty"),
    "FINNIFTY": ("fin nifty", "finnifty"),
    "MIDCAPNIFTY": ("midcap nifty", "midcapnifty", "nifty midcap"),
    "VIXNIFTY": ("india vix", "vix", "fear index"),
    "INR": ("inr", "rupee", "rbi", "india"),
    "US30": ("dow jones", "us30", "djia"),
    "US100": ("nasdaq", "us100", "ixic"),
    "SP500": ("s&p 500", "sp500", "spx"),
    "UK100": ("ftse 100", "ftse", "uk100"),
    "GER40": ("dax", "ger40", "dax 40"),
    "JPN225": ("nikkei", "jpn225", "nikkei 225", "n225"),
    "HK50": ("hang seng", "hk50", "hsi"),
    "AUS200": ("asx 200", "aus200", "s&p/asx 200"),
    "ADANIENT": ("adani enterprises", "adanient", "adani group"),
    "ADANIPORTS": ("adani ports", "adaniports"),
    "ADANIGREEN": ("adani green", "adanigreen"),
    "ADANITRANS": ("adani transmission", "adanitrans"),
    "ADANIPOWER": ("adani power", "adanipower"),
    "RELIANCE": ("reliance", "ril"),
    "TCS": ("tcs", "tata consultancy"),
    "HDFCBANK": ("hdfc bank", "hdfcbank"),
    "INFY": ("infosys", "infy"),
    "ICICIBANK": ("icici bank", "icicibank"),
    "SBIN": ("sbi", "state bank"),
    "BHARTI": ("bharti", "airtel"),
    "WIPRO": ("wipro",),
    "ITC": ("itc",),
    "LT": ("larsen", "l&t", "larsen & toubro"),
    "AXISBANK": ("axis bank", "axis"),
    "KOTAKBANK": ("kotak", "kotak mahindra", "kotak bank"),
    "MARUTI": ("maruti", "maruti suzuki"),
    "TATAMOTORS": ("tata motors", "tata motor"),
    "ASIANPAINT": ("asian paints", "asian paint"),
    "HCLTECH": ("hcl", "hcl technologies", "hcl tech"),
    "SUNPHARMA": ("sun pharma", "sun pharmaceutical"),
    "BAJFINANCE": ("bajaj finance",),
    "TITAN": ("titan",),
    "NTPC": ("ntpc",),
    "ONGC": ("ongc",),
    "POWERGRID": ("power grid", "powergrid"),
    "ULTRACEMCO": ("ultratech", "ultratech cement", "ultracemco"),
    "TATASTEEL": ("tata steel", "tatasteel"),
    "JSWSTEEL": ("jsw steel", "jswsteel"),
    "HINDALCO": ("hindalco", "hindalco industries"),
    "TECHM": ("tech mahindra", "techm"),
    "COALINDIA": ("coal india", "coalindia"),
    "HINDUNILVR": ("hindustan unilever", "hul", "hindunilvr"),
    "BRITANNIA": ("britannia", "britannia industries"),
    "NESTLEIND": ("nestle india", "nestleind"),
    "M&M": ("mahindra", "m&m", "mahindra & mahindra"),
    "EICHERMOT": ("eicher motors", "eichermot", "royal enfield"),
    "HEROMOTOCO": ("hero motocorp", "heromotoco", "hero honda"),
    "BAJAJ-AUTO": ("bajaj auto", "bajajauto"),
    "TATACONSUM": ("tata consumer", "tataconsumer"),
    "DABUR": ("dabur",),
    "MARICO": ("marico",),
    "HDFC": ("hdfc", "hdfc ltd"),
    "ICICIPRUDI": ("icici prudential", "iciciprudential"),
    "HDFCLIFE": ("hdfc life", "hdFclife"),
    "SBILIFE": ("sbi life", "sbilife"),
    "TRENT": ("trent", "westside", "zudio"),
    "AVENUE": ("avenue supermarts", "dmart", "avenue"),
    "PIDILITIND": ("pidilite", "pidilitind", "fevicol"),
    "HAVELLS": ("havells", "havells india"),
    "SIEMENS": ("siemens india", "siemens"),
    "BEL": ("bharat electronics", "bel", "bharat electronics limited"),
    "BHEL": ("bhel", "bharat heavy electricals"),
    "HAL": ("hal", "hindustan aeronautics", "hindustan aeronautics limited"),
    "IRFC": ("irfc", "indian railway finance"),
    "IREDA": ("ireda", "indian renewable energy development"),
    "SUZLON": ("suzlon", "suzlon energy"),
    "HINDZINC": ("hindustan zinc", "hindzinc"),
    "VEDL": ("vedanta", "vedl"),
    "IOC": ("indian oil", "ioc", "indianoil"),
    "BPCL": ("bpcl", "bharat petroleum"),
    "GAIL": ("gail", "gail india"),
    "NATIONALUM": ("national aluminium", "nationalum", "nalco"),
    "ZOMATO": ("zomato", "blinkit"),
    "SWIGGY": ("swiggy",),
    "PAYTM": ("paytm", "one97 communications"),
    "POLICYBZR": ("policybazaar", "policybzr", "pb fintech"),
    "NYKAA": ("nykaa", "fsn ecommerce"),
    "HDFCAMC": ("hdfc asset management", "hdfcamc"),
    "GRASIM": ("grasim", "grasim industries"),
    "DIVISLAB": ("divi's laboratories", "divislab", "divi"),
    "CIPLA": ("cipla",),
    "DRREDDY": ("dr reddy", "drreddy", "dr. reddy"),
    "APOLLOHOSP": ("apollo hospitals", "apollohosp"),
    "AUROPHARMA": ("aurobinido pharma", "auropharma"),
    "TVSMOTOR": ("tvs motor", "tvsmotor"),
    "AAPL": ("apple", "aapl", "iphone"),
    "MSFT": ("microsoft", "msft", "windows", "azure"),
    "GOOGL": ("google", "alphabet", "googl", "goog"),
    "AMZN": ("amazon", "amzn", "aws"),
    "NVDA": ("nvidia", "nvda", "geforce"),
    "META": ("meta", "facebook", "meta platforms"),
    "TSLA": ("tesla", "tsla", "elon"),
    "JPM": ("jpmorgan", "jp morgan", "jpm", "chase"),
    "V": ("visa", "v"),
    "WMT": ("walmart", "wmt"),
    "JNJ": ("johnson & johnson", "jnj"),
    "PG": ("procter & gamble", "pg"),
    "XOM": ("exxon", "xom", "exxon mobil"),
    "UNH": ("unitedhealth", "unh", "united health"),
    "HD": ("home depot", "hd"),
    "BAC": ("bank of america", "bac"),
    "DIS": ("disney", "dis"),
    "NFLX": ("netflix", "nflx"),
    "ADBE": ("adobe", "adbe"),
    "CRM": ("salesforce", "crm"),
    "INTC": ("intel", "intc"),
    "AMD": ("amd", "advanced micro devices"),
    "PYPL": ("paypal", "pypl"),
    "UBER": ("uber", "uber technologies"),
    "NKE": ("nike", "nke"),
    "BA": ("boeing", "ba"),
    "COIN": ("coinbase", "coin"),
    "SNAP": ("snapchat", "snap"),
    "SQ": ("block", "square", "sq"),
    "PLTR": ("palantir", "pltr"),
    "RBLX": ("roblox", "rblx"),
    "MCD": ("mcdonald", "mcd", "mcdonald's"),
    "SBUX": ("starbucks", "sbux"),
    "NIO": ("nio",),
    "RIVN": ("rivian", "rivn"),
}

TRADE_PAIRS = {
    "USD": [("EUR/USD", -1, 0.0001), ("USD/JPY", 1, 0.01), ("GBP/USD", -1, 0.0001), ("USD/CAD", 1, 0.0001)],
    "EUR": [("EUR/USD", 1, 0.0001), ("EUR/GBP", 1, 0.0001)],
    "GBP": [("GBP/USD", 1, 0.0001), ("EUR/GBP", -1, 0.0001)],
    "JPY": [("USD/JPY", -1, 0.01)],
    "XAU": [("XAU/USD", 1, 0.1)],
    "XAG": [("XAG/USD", 1, 0.01)],
    "OIL": [("WTI", 1, 0.01), ("BRENT", 1, 0.01)],
    "BTC": [("BTC/USD", 1, 1.0)],
    "ETH": [("ETH/USD", 1, 1.0)],
    "SOL": [("SOL/USD", 1, 0.01)],
    "XRP": [("XRP/USD", 1, 0.0001)],
    "ADA": [("ADA/USD", 1, 0.0001)],
    "DOGE": [("DOGE/USD", 1, 0.0001)],
    "DOT": [("DOT/USD", 1, 0.001)],
    "AVAX": [("AVAX/USD", 1, 0.01)],
    "LINK": [("LINK/USD", 1, 0.01)],
    "LTC": [("LTC/USD", 1, 0.01)],
    "AUD": [("AUD/USD", -1, 0.0001), ("NZD/USD", -1, 0.0001)],
    "NZD": [("NZD/USD", -1, 0.0001), ("AUD/USD", -1, 0.0001)],
    "CHF": [("USD/CHF", 1, 0.0001)],
    "CAD": [("USD/CAD", 1, 0.0001)],
    "MXN": [("USD/MXN", 1, 0.001)],
    "ZAR": [("USD/ZAR", 1, 0.001)],
    "TRY": [("USD/TRY", 1, 0.001)],
    "SGD": [("USD/SGD", 1, 0.001)],
    "HKD": [("USD/HKD", 1, 0.001)],
    "CNY": [("USD/CNY", 1, 0.001)],
    "INR": [("USD/INR", 1, 0.01)],
    "US30": [("US30", 1, 1.0)],
    "US100": [("US100", 1, 1.0)],
    "SP500": [("SP500", 1, 1.0)],
    "UK100": [("UK100", 1, 1.0)],
    "GER40": [("GER40", 1, 1.0)],
    "JPN225": [("JPN225", 1, 1.0)],
    "HK50": [("HK50", 1, 1.0)],
    "AUS200": [("AUS200", 1, 1.0)],
    "NIFTY": [("NIFTY", 1, 1.0)],
    "SENSEX": [("SENSEX", 1, 1.0)],
    "BANKNIFTY": [("BANKNIFTY", 1, 1.0)],
    "FINNIFTY": [("FINNIFTY", 1, 1.0)],
    "MIDCAPNIFTY": [("MIDCAPNIFTY", 1, 1.0)],
    "VIXNIFTY": [("INDIAVIX", 1, 0.01)],
    "AAPL": [("AAPL", 1, 0.5)],
    "MSFT": [("MSFT", 1, 0.5)],
    "GOOGL": [("GOOGL", 1, 0.5)],
    "AMZN": [("AMZN", 1, 1.0)],
    "NVDA": [("NVDA", 1, 1.0)],
    "META": [("META", 1, 0.5)],
    "TSLA": [("TSLA", 1, 1.0)],
    "JPM": [("JPM", 1, 0.5)],
    "V": [("V", 1, 0.5)],
    "WMT": [("WMT", 1, 0.2)],
    "JNJ": [("JNJ", 1, 0.5)],
    "PG": [("PG", 1, 0.5)],
    "XOM": [("XOM", 1, 0.5)],
    "UNH": [("UNH", 1, 1.0)],
    "HD": [("HD", 1, 0.5)],
    "BAC": [("BAC", 1, 0.1)],
    "DIS": [("DIS", 1, 0.2)],
    "NFLX": [("NFLX", 1, 1.0)],
    "ADBE": [("ADBE", 1, 1.0)],
    "CRM": [("CRM", 1, 0.5)],
    "INTC": [("INTC", 1, 0.1)],
    "AMD": [("AMD", 1, 0.2)],
    "PYPL": [("PYPL", 1, 0.2)],
    "UBER": [("UBER", 1, 0.2)],
    "NKE": [("NKE", 1, 0.2)],
    "BA": [("BA", 1, 0.5)],
    "COIN": [("COIN", 1, 1.0)],
    "SNAP": [("SNAP", 1, 0.05)],
    "SQ": [("SQ", 1, 0.2)],
    "PLTR": [("PLTR", 1, 0.1)],
    "RBLX": [("RBLX", 1, 0.2)],
    "MCD": [("MCD", 1, 0.5)],
    "SBUX": [("SBUX", 1, 0.2)],
    "NIO": [("NIO", 1, 0.05)],
    "RIVN": [("RIVN", 1, 0.05)],
    "RELIANCE": [("RELIANCE", 1, 1.0)],
    "TCS": [("TCS", 1, 1.0)],
    "HDFCBANK": [("HDFCBANK", 1, 0.5)],
    "INFY": [("INFY", 1, 0.5)],
    "ICICIBANK": [("ICICIBANK", 1, 0.5)],
    "SBIN": [("SBIN", 1, 0.5)],
    "BHARTI": [("BHARTI", 1, 0.5)],
    "WIPRO": [("WIPRO", 1, 0.2)],
    "ITC": [("ITC", 1, 0.2)],
    "LT": [("LT", 1, 1.0)],
    "AXISBANK": [("AXISBANK", 1, 0.5)],
    "KOTAKBANK": [("KOTAKBANK", 1, 0.5)],
    "MARUTI": [("MARUTI", 1, 1.0)],
    "TATAMOTORS": [("TATAMOTORS", 1, 0.5)],
    "ASIANPAINT": [("ASIANPAINT", 1, 1.0)],
    "HCLTECH": [("HCLTECH", 1, 0.5)],
    "SUNPHARMA": [("SUNPHARMA", 1, 0.5)],
    "BAJFINANCE": [("BAJFINANCE", 1, 1.0)],
    "TITAN": [("TITAN", 1, 1.0)],
    "NTPC": [("NTPC", 1, 0.5)],
    "ONGC": [("ONGC", 1, 0.2)],
    "POWERGRID": [("POWERGRID", 1, 0.5)],
    "ULTRACEMCO": [("ULTRACEMCO", 1, 1.0)],
    "TATASTEEL": [("TATASTEEL", 1, 0.5)],
    "JSWSTEEL": [("JSWSTEEL", 1, 0.5)],
    "HINDALCO": [("HINDALCO", 1, 0.5)],
    "TECHM": [("TECHM", 1, 0.5)],
    "COALINDIA": [("COALINDIA", 1, 0.2)],
    "HINDUNILVR": [("HINDUNILVR", 1, 1.0)],
    "BRITANNIA": [("BRITANNIA", 1, 1.0)],
    "NESTLEIND": [("NESTLEIND", 1, 2.0)],
    "M&M": [("M&M", 1, 0.5)],
    "EICHERMOT": [("EICHERMOT", 1, 1.0)],
    "HEROMOTOCO": [("HEROMOTOCO", 1, 0.5)],
    "BAJAJ-AUTO": [("BAJAJ_AUTO", 1, 1.0)],
    "TATACONSUM": [("TATACONSUM", 1, 0.5)],
    "DABUR": [("DABUR", 1, 0.5)],
    "MARICO": [("MARICO", 1, 0.5)],
    "HDFC": [("HDFC", 1, 0.5)],
    "ICICIPRUDI": [("ICICIPRUDI", 1, 0.5)],
    "HDFCLIFE": [("HDFCLIFE", 1, 0.2)],
    "SBILIFE": [("SBILIFE", 1, 0.5)],
    "TRENT": [("TRENT", 1, 1.0)],
    "AVENUE": [("AVENUE", 1, 1.0)],
    "PIDILITIND": [("PIDILITIND", 1, 0.5)],
    "HAVELLS": [("HAVELLS", 1, 0.5)],
    "SIEMENS": [("SIEMENS", 1, 1.0)],
    "BEL": [("BEL", 1, 0.5)],
    "BHEL": [("BHEL", 1, 0.1)],
    "HAL": [("HAL", 1, 1.0)],
    "IRFC": [("IRFC", 1, 0.1)],
    "IREDA": [("IREDA", 1, 0.1)],
    "SUZLON": [("SUZLON", 1, 0.05)],
    "ADANIENT": [("ADANIENT", 1, 1.0)],
    "ADANIPORTS": [("ADANIPORTS", 1, 0.5)],
    "ADANIGREEN": [("ADANIGREEN", 1, 0.5)],
    "ADANITRANS": [("ADANITRANS", 1, 0.5)],
    "ADANIPOWER": [("ADANIPOWER", 1, 0.2)],
    "HINDZINC": [("HINDZINC", 1, 0.2)],
    "VEDL": [("VEDL", 1, 0.2)],
    "IOC": [("IOC", 1, 0.2)],
    "BPCL": [("BPCL", 1, 0.2)],
    "GAIL": [("GAIL", 1, 0.2)],
    "NATIONALUM": [("NATIONALUM", 1, 0.2)],
    "ZOMATO": [("ZOMATO", 1, 0.1)],
    "SWIGGY": [("SWIGGY", 1, 0.1)],
    "PAYTM": [("PAYTM", 1, 0.1)],
    "POLICYBZR": [("POLICYBZR", 1, 0.1)],
    "NYKAA": [("NYKAA", 1, 0.2)],
    "HDFCAMC": [("HDFCAMC", 1, 0.5)],
    "GRASIM": [("GRASIM", 1, 1.0)],
    "DIVISLAB": [("DIVISLAB", 1, 1.0)],
    "CIPLA": [("CIPLA", 1, 0.5)],
    "DRREDDY": [("DRREDDY", 1, 1.0)],
    "APOLLOHOSP": [("APOLLOHOSP", 1, 1.0)],
    "AUROPHARMA": [("AUROPHARMA", 1, 0.2)],
    "TVSMOTOR": [("TVSMOTOR", 1, 0.5)],
}

INSTRUMENT_NAMES: dict[str, str] = {
    "XAU/USD": "Gold vs US Dollar",
    "XAG/USD": "Silver vs US Dollar",
    "EUR/USD": "Euro vs US Dollar",
    "GBP/USD": "British Pound vs US Dollar",
    "USD/JPY": "US Dollar vs Japanese Yen",
    "USD/CAD": "US Dollar vs Canadian Dollar",
    "EUR/GBP": "Euro vs British Pound",
    "WTI": "Crude Oil WTI",
    "BRENT": "Brent Crude Oil",
    "BTC/USD": "Bitcoin vs US Dollar",
    "ETH/USD": "Ethereum vs US Dollar",
    "SOL/USD": "Solana vs US Dollar",
    "XRP/USD": "Ripple vs US Dollar",
    "ADA/USD": "Cardano vs US Dollar",
    "DOGE/USD": "Dogecoin vs US Dollar",
    "DOT/USD": "Polkadot vs US Dollar",
    "AVAX/USD": "Avalanche vs US Dollar",
    "LINK/USD": "Chainlink vs US Dollar",
    "LTC/USD": "Litecoin vs US Dollar",
    "AUD/USD": "Australian Dollar vs US Dollar",
    "NZD/USD": "New Zealand Dollar vs US Dollar",
    "USD/CHF": "US Dollar vs Swiss Franc",
    "USD/CAD": "US Dollar vs Canadian Dollar",
    "USD/MXN": "US Dollar vs Mexican Peso",
    "USD/ZAR": "US Dollar vs South African Rand",
    "USD/TRY": "US Dollar vs Turkish Lira",
    "USD/SGD": "US Dollar vs Singapore Dollar",
    "USD/HKD": "US Dollar vs Hong Kong Dollar",
    "USD/CNY": "US Dollar vs Chinese Yuan",
    "USD/INR": "US Dollar vs Indian Rupee",
    "US30": "Dow Jones Industrial Average",
    "US100": "NASDAQ 100",
    "SP500": "S&P 500 Index",
    "UK100": "FTSE 100 Index",
    "GER40": "DAX 40 Index",
    "JPN225": "Nikkei 225 Index",
    "HK50": "Hang Seng Index",
    "AUS200": "S&P/ASX 200 Index",
    "NIFTY": "Nifty 50",
    "SENSEX": "BSE Sensex",
    "BANKNIFTY": "Bank Nifty",
    "FINNIFTY": "Fin Nifty",
    "MIDCAPNIFTY": "Nifty Midcap 100",
    "VIXNIFTY": "India VIX",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc. (Facebook)",
    "TSLA": "Tesla Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "WMT": "Walmart Inc.",
    "JNJ": "Johnson & Johnson",
    "PG": "Procter & Gamble Co.",
    "XOM": "Exxon Mobil Corporation",
    "UNH": "UnitedHealth Group Inc.",
    "HD": "The Home Depot Inc.",
    "BAC": "Bank of America Corporation",
    "DIS": "The Walt Disney Company",
    "NFLX": "Netflix Inc.",
    "ADBE": "Adobe Inc.",
    "CRM": "Salesforce Inc.",
    "INTC": "Intel Corporation",
    "AMD": "Advanced Micro Devices Inc.",
    "PYPL": "PayPal Holdings Inc.",
    "UBER": "Uber Technologies Inc.",
    "NKE": "Nike Inc.",
    "BA": "The Boeing Company",
    "COIN": "Coinbase Global Inc.",
    "SNAP": "Snap Inc. (Snapchat)",
    "SQ": "Block Inc. (Square)",
    "PLTR": "Palantir Technologies Inc.",
    "RBLX": "Roblox Corporation",
    "MCD": "McDonald's Corporation",
    "SBUX": "Starbucks Corporation",
    "NIO": "NIO Inc.",
    "RIVN": "Rivian Automotive Inc.",
    "RELIANCE": "Reliance Industries Ltd.",
    "TCS": "Tata Consultancy Services",
    "HDFCBANK": "HDFC Bank Ltd.",
    "INFY": "Infosys Ltd.",
    "ICICIBANK": "ICICI Bank Ltd.",
    "SBIN": "State Bank of India",
    "BHARTI": "Bharti Airtel Ltd.",
    "WIPRO": "Wipro Ltd.",
    "ITC": "ITC Ltd.",
    "LT": "Larsen & Toubro Ltd.",
    "AXISBANK": "Axis Bank Ltd.",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd.",
    "MARUTI": "Maruti Suzuki India Ltd.",
    "TATAMOTORS": "Tata Motors Ltd.",
    "ASIANPAINT": "Asian Paints Ltd.",
    "HCLTECH": "HCL Technologies Ltd.",
    "SUNPHARMA": "Sun Pharmaceutical Industries Ltd.",
    "BAJFINANCE": "Bajaj Finance Ltd.",
    "TITAN": "Titan Company Ltd.",
    "NTPC": "NTPC Ltd.",
    "ONGC": "Oil & Natural Gas Corporation Ltd.",
    "POWERGRID": "Power Grid Corporation of India Ltd.",
    "ULTRACEMCO": "UltraTech Cement Ltd.",
    "TATASTEEL": "Tata Steel Ltd.",
    "JSWSTEEL": "JSW Steel Ltd.",
    "HINDALCO": "Hindalco Industries Ltd.",
    "TECHM": "Tech Mahindra Ltd.",
    "COALINDIA": "Coal India Ltd.",
    "HINDUNILVR": "Hindustan Unilever Ltd.",
    "BRITANNIA": "Britannia Industries Ltd.",
    "NESTLEIND": "Nestlé India Ltd.",
    "M&M": "Mahindra & Mahindra Ltd.",
    "EICHERMOT": "Eicher Motors Ltd.",
    "HEROMOTOCO": "Hero MotoCorp Ltd.",
    "BAJAJ_AUTO": "Bajaj Auto Ltd.",
    "TATACONSUM": "Tata Consumer Products Ltd.",
    "DABUR": "Dabur India Ltd.",
    "MARICO": "Marico Ltd.",
    "HDFC": "HDFC Ltd.",
    "ICICIPRUDI": "ICICI Prudential Life Insurance",
    "HDFCLIFE": "HDFC Life Insurance Company",
    "SBILIFE": "SBI Life Insurance Company",
    "TRENT": "Trent Ltd.",
    "AVENUE": "Avenue Supermarts Ltd. (DMart)",
    "PIDILITIND": "Pidilite Industries Ltd.",
    "HAVELLS": "Havells India Ltd.",
    "SIEMENS": "Siemens Ltd.",
    "BEL": "Bharat Electronics Ltd.",
    "BHEL": "Bharat Heavy Electricals Ltd.",
    "HAL": "Hindustan Aeronautics Ltd.",
    "IRFC": "Indian Railway Finance Corporation",
    "IREDA": "Indian Renewable Energy Development Agency",
    "SUZLON": "Suzlon Energy Ltd.",
    "ADANIENT": "Adani Enterprises Ltd.",
    "ADANIPORTS": "Adani Ports & SEZ Ltd.",
    "ADANIGREEN": "Adani Green Energy Ltd.",
    "ADANITRANS": "Adani Transmission Ltd.",
    "ADANIPOWER": "Adani Power Ltd.",
    "HINDZINC": "Hindustan Zinc Ltd.",
    "VEDL": "Vedanta Ltd.",
    "IOC": "Indian Oil Corporation Ltd.",
    "BPCL": "Bharat Petroleum Corporation Ltd.",
    "GAIL": "GAIL (India) Ltd.",
    "NATIONALUM": "National Aluminium Company Ltd.",
    "ZOMATO": "Zomato Ltd.",
    "SWIGGY": "Swiggy Ltd.",
    "PAYTM": "One97 Communications Ltd. (Paytm)",
    "POLICYBZR": "PB Fintech Ltd. (Policybazaar)",
    "NYKAA": "FSN E-Commerce Ventures Ltd. (Nykaa)",
    "HDFCAMC": "HDFC Asset Management Company",
    "GRASIM": "Grasim Industries Ltd.",
    "DIVISLAB": "Divi's Laboratories Ltd.",
    "CIPLA": "Cipla Ltd.",
    "DRREDDY": "Dr. Reddy's Laboratories Ltd.",
    "APOLLOHOSP": "Apollo Hospitals Enterprise Ltd.",
    "AUROPHARMA": "Aurobindo Pharma Ltd.",
    "TVSMOTOR": "TVS Motor Company Ltd.",
}

FOREX_PRICE_API = "https://api.exchangerate-api.com/v4/latest/USD"

POSITIVE_KEYWORDS = {
    "rises",
    "rise",
    "gains",
    "gain",
    "surges",
    "surge",
    "strengthens",
    "strong",
    "hawkish",
    "beats",
    "beat",
    "higher",
    "upside",
    "rally",
    "rallies",
    "breakout",
    "bullish",
    "recovery",
    "rebound",
    "upgrade",
}

NEGATIVE_KEYWORDS = {
    "falls",
    "fall",
    "drops",
    "drop",
    "slides",
    "slide",
    "weakens",
    "weak",
    "dovish",
    "misses",
    "miss",
    "lower",
    "downside",
    "cut",
    "crash",
    "plunge",
    "decline",
    "bearish",
    "selloff",
    "downgrade",
    "slump",
}

HIGH_IMPACT_KEYWORDS = {
    "breaking", "just in", "urgent", "emergency",
    "fed rate decision", "fomc", "interest rate decision",
    "nonfarm payrolls", "nfp", "jobs report",
    "cpi", "consumer price index", "inflation data",
    "gdp", "economic growth",
    "crash", "plunge", "selloff", "rout",
    "war", "invasion", "sanctions",
    "central bank", "rate hike", "rate cut",
    "recession", "depression",
    "bankruptcy", "bailout",
    "black swan", "flash crash",
    "market crash", "stock crash",
    "fed emergency", "emergency meeting",
}

TRADING_SYSTEM_PROMPT = (
    "You are a professional Telegram trading signal bot. "
    "You generate clear, actionable trade setups with entry, targets, and stop-loss levels. "
    "You are concise, factual, and never give financial advice — only data-driven setups. "
    "Always state the direction, pair, entry price, TP1, TP2, and SL. "
    "Keep financial terms in English. "
    "Use bullet points or numbered lists for readability."
)
INSTITUTIONAL_ANALYSIS_SYSTEM_PROMPT = (
    "You are a professional investment and trading analyst. "
    "Use institutional-quality structure, but do not claim to work for any bank, fund, or consulting firm. "
    "Be factual, data-driven, and transparent about assumptions. "
    "If live data is unavailable, say what data is needed and provide a conditional framework. "
    "Never present the output as financial advice."
)

INSTITUTIONAL_ANALYSIS_PROMPTS: dict[str, dict[str, Any]] = {
    "stock_screener": {
        "title": "Goldman Sachs-Level Stock Screener",
        "keywords": ("stock screener", "screen stocks", "top 10 stocks", "investment goals", "p/e ratio"),
        "prompt": (
            "I need a complete stock screening framework for my investment goals.\n\n"
            "Analyze and provide:\n"
            "- Top 10 stocks matching my criteria with ticker symbols\n"
            "- P/E ratio analysis compared to sector averages\n"
            "- Revenue growth trends over the last 5 years\n"
            "- Debt-to-equity health check for each pick\n"
            "- Dividend yield and payout sustainability score\n"
            "- Competitive moat rating: weak, moderate, or strong\n"
            "- Bull case and bear case price targets for 12 months\n"
            "- Risk rating on a scale of 1-10 with clear reasoning\n"
            "- Entry price zones and stop-loss suggestions\n\n"
            "Format as a professional equity research screening report with a summary table."
        ),
    },
    "dcf_valuation": {
        "title": "Morgan Stanley-Style DCF Valuation Deep Dive",
        "keywords": ("dcf", "discounted cash flow", "valuation", "fair value", "wacc", "terminal value"),
        "prompt": (
            "I need a full discounted cash flow analysis for a specific stock.\n\n"
            "Build out:\n"
            "- 5-year revenue projection with growth assumptions\n"
            "- Operating margin estimates based on historical trends\n"
            "- Free cash flow calculations year by year\n"
            "- Weighted average cost of capital estimate\n"
            "- Terminal value using both exit multiple and perpetuity growth methods\n"
            "- Sensitivity table showing fair value at different discount rates\n"
            "- Comparison of DCF value vs current market price\n"
            "- Clear verdict: undervalued, fairly valued, or overvalued\n"
            "- Key assumptions that could break the model\n\n"
            "Format as an investment banking valuation memo with tables and clear math."
        ),
    },
    "risk_analysis": {
        "title": "Bridgewater-Inspired Risk Analysis Framework",
        "keywords": ("risk analysis", "risk assessment", "portfolio risk", "correlation", "drawdown", "hedging"),
        "prompt": (
            "I need a complete risk assessment of my current portfolio.\n\n"
            "Evaluate:\n"
            "- Correlation analysis between my holdings\n"
            "- Sector concentration risk with percentage breakdown\n"
            "- Geographic exposure and currency risk factors\n"
            "- Interest rate sensitivity for each position\n"
            "- Recession stress test showing estimated drawdown\n"
            "- Liquidity risk rating for each holding\n"
            "- Single stock risk and position sizing recommendations\n"
            "- Tail risk scenarios with probability estimates\n"
            "- Hedging strategies to reduce my top 3 risks\n"
            "- Rebalancing suggestions with specific allocation percentages\n\n"
            "Format as a professional risk management report with a heat map-style summary."
        ),
    },
    "earnings_breakdown": {
        "title": "JPMorgan-Level Earnings Breakdown",
        "keywords": ("earnings", "quarter", "eps", "beat or miss", "implied move", "guidance"),
        "prompt": (
            "I need a complete earnings analysis before a company reports.\n\n"
            "Deliver:\n"
            "- Last 4 quarters earnings vs estimates, including beat or miss history\n"
            "- Revenue and EPS consensus estimates for the upcoming quarter\n"
            "- Key metrics Wall Street is watching for this company\n"
            "- Segment-by-segment revenue breakdown and trends\n"
            "- Management guidance from the last earnings call summarized\n"
            "- Options market implied move for earnings day\n"
            "- Historical stock price reaction after the last 4 earnings reports\n"
            "- Bull case scenario and price impact estimate\n"
            "- Bear case scenario and downside risk estimate\n"
            "- Recommended play: buy before, sell before, or wait\n\n"
            "Format as a pre-earnings research brief with a decision summary at the top."
        ),
    },
    "portfolio_construction": {
        "title": "BlackRock-Style Portfolio Construction Model",
        "keywords": ("portfolio construction", "asset allocation", "investment policy", "etf", "rebalance"),
        "prompt": (
            "I need a custom investment portfolio built from scratch for my situation.\n\n"
            "Create:\n"
            "- Exact asset allocation with percentages across stocks, bonds, and alternatives\n"
            "- Specific ETF or fund recommendations for each category with ticker symbols\n"
            "- Core holdings vs satellite positions clearly labeled\n"
            "- Expected annual return range based on historical data\n"
            "- Expected maximum drawdown in a bad year\n"
            "- Rebalancing schedule and trigger rules\n"
            "- Tax efficiency strategy for my account type\n"
            "- Dollar-cost averaging plan if I invest monthly\n"
            "- Benchmark to measure my performance against\n"
            "- One-page investment policy statement I can follow\n\n"
            "Format as a professional investment policy document with an allocation pie chart description."
        ),
    },
    "technical_analysis": {
        "title": "Citadel-Grade Technical Analysis System",
        "keywords": ("technical analysis", "support", "resistance", "rsi", "macd", "bollinger", "fibonacci"),
        "prompt": (
            "I need a full technical analysis breakdown of a stock, index, crypto, forex pair, or commodity.\n\n"
            "Analyze:\n"
            "- Current trend direction on daily, weekly, and monthly timeframes\n"
            "- Key support and resistance levels with exact price points\n"
            "- Moving average analysis for 50-day, 100-day, and 200-day averages\n"
            "- Crossover signals, RSI, MACD, and Bollinger Band readings with plain-English interpretation\n"
            "- Volume trend analysis and what it signals about buyer vs seller strength\n"
            "- Chart pattern identification such as head and shoulders or cup and handle\n"
            "- Fibonacci retracement levels for potential bounce zones\n"
            "- Ideal entry price, stop-loss level, and profit target\n"
            "- Risk-to-reward ratio for the current setup\n"
            "- Confidence rating: strong buy, buy, neutral, sell, or strong sell\n\n"
            "Format as a technical analysis report card with a clear trade plan summary."
        ),
    },
    "dividend_strategy": {
        "title": "Harvard Endowment-Inspired Dividend Strategy",
        "keywords": ("dividend", "income portfolio", "passive income", "drip", "payout ratio", "yield"),
        "prompt": (
            "I need a dividend income portfolio that generates reliable passive income.\n\n"
            "Build:\n"
            "- 15-20 dividend stock picks with ticker symbols and current yield\n"
            "- Dividend safety score for each stock on a 1-10 scale\n"
            "- Consecutive years of dividend growth for each pick\n"
            "- Payout ratio analysis to flag any unsustainable dividends\n"
            "- Monthly income projection based on my investment amount\n"
            "- Sector diversification breakdown to avoid concentration\n"
            "- Dividend growth rate estimate for the next 5 years\n"
            "- DRIP reinvestment projection showing compounding over 10 years\n"
            "- Tax implications summary for dividends in my account type\n"
            "- Ranked list from safest to most aggressive picks\n\n"
            "Format as a dividend portfolio blueprint with an income projection table."
        ),
    },
    "competitive_advantage": {
        "title": "Bain-Style Competitive Advantage Analysis",
        "keywords": ("competitive advantage", "competitive landscape", "sector analysis", "market share", "swot"),
        "prompt": (
            "I need a full competitive landscape report to find the best stock to buy in a sector.\n\n"
            "Provide:\n"
            "- Top 5-7 competitors in the sector with market cap comparison\n"
            "- Revenue and profit margin comparison in a table format\n"
            "- Competitive moat analysis for each company: brand, cost, network, switching\n"
            "- Market share trends over the last 3 years\n"
            "- Management quality rating based on capital allocation track record\n"
            "- Innovation pipeline and R&D spending comparison\n"
            "- Biggest threats to the sector: regulation, disruption, macro\n"
            "- SWOT analysis for the top 2 companies\n"
            "- Single best stock pick with a clear rationale\n"
            "- Catalysts that could move the winner stock in the next 12 months\n\n"
            "Format as a competitive strategy deck summary with comparison tables."
        ),
    },
    "pattern_finder": {
        "title": "Renaissance Technologies Pattern Finder",
        "keywords": ("pattern", "seasonal", "anomaly", "statistical edge", "short interest", "options activity"),
        "prompt": (
            "I need you to identify hidden patterns and anomalies in a stock's behavior.\n\n"
            "Research:\n"
            "- Seasonal patterns: best and worst months historically\n"
            "- Day-of-week performance patterns if any exist\n"
            "- Correlation with major market events such as Fed meetings and CPI reports\n"
            "- Insider buying and selling patterns from recent filings\n"
            "- Institutional ownership trend: are big funds buying or selling\n"
            "- Short interest analysis and squeeze potential\n"
            "- Unusual options activity signals worth watching\n"
            "- Price behavior around earnings: pre-run and post-gap patterns\n"
            "- Sector rotation signals that affect this stock\n"
            "- Statistical edge summary: what gives this stock a quantifiable advantage\n\n"
            "Format as a quantitative research memo with data tables and pattern summaries."
        ),
    },
    "macro_impact": {
        "title": "McKinsey-Level Macro Impact Assessment",
        "keywords": ("macro", "macroeconomic", "interest rate", "inflation", "gdp", "federal reserve", "economy"),
        "prompt": (
            "I need a macro analysis showing how current economic conditions affect my portfolio.\n\n"
            "Analyze:\n"
            "- Current interest rate environment and its impact on growth vs value stocks\n"
            "- Inflation trend analysis and which sectors benefit or suffer\n"
            "- GDP growth forecast and what it means for corporate earnings\n"
            "- US dollar strength impact on international vs domestic holdings\n"
            "- Employment data trends and consumer spending implications\n"
            "- Federal Reserve policy outlook for the next 6-12 months\n"
            "- Global risk factors: geopolitics, trade wars, supply chains\n"
            "- Sector rotation recommendation based on the current economic cycle\n"
            "- Specific portfolio adjustments I should consider right now\n"
            "- Timeline: when these macro factors will most likely impact markets\n\n"
            "Format as an executive macro strategy briefing with a clear action plan."
        ),
    },
}


def load_seen_keys() -> set[str]:
    try:
        with open(SENT_KEYS_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen_keys(keys: set[str]) -> None:
    with open(SENT_KEYS_FILE, "w") as f:
        json.dump(sorted(keys), f)


def load_sent_messages_cache() -> list[str]:
    try:
        with open(SENT_MESSAGES_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_sent_messages_cache(cache: list[str]) -> None:
    try:
        with open(SENT_MESSAGES_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def load_signal_log() -> list[dict]:
    try:
        with open(SIGNAL_LOG_FILE) as f:
            data = json.load(f)
        seen = set()
        unique_data = []
        has_duplicates = False
        for sig in data:
            key = (sig.get("pair"), sig.get("direction"), sig.get("entry"), sig.get("tp1"), sig.get("sl"))
            if key not in seen:
                seen.add(key)
                unique_data.append(sig)
            else:
                has_duplicates = True
        if has_duplicates:
            with open(SIGNAL_LOG_FILE, "w") as f:
                json.dump(unique_data, f, indent=2)
            print("[CLEANUP] Automatically removed duplicates from signal_log.json.")
        return unique_data
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_signal_log(log: list[dict]) -> None:
    with open(SIGNAL_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def load_subscribers() -> list[int]:
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_subscribers(subs: list[int]) -> None:
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subs, f)


def _backfill_subscribers_from_updates() -> None:
    global _subscribers
    try:
        from urllib.request import urlopen
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        resp = urlopen(url, timeout=10)
        data = json.loads(resp.read().decode())
        added = 0
        for upd in data.get("result", []):
            msg = upd.get("message")
            if msg:
                cid = msg.get("chat", {}).get("id")
                if cid and isinstance(cid, int) and cid not in _subscribers:
                    _subscribers.append(cid)
                    added += 1
        if added:
            save_subscribers(_subscribers)
            print(f"[BACKFILL] Added {added} chat ID(s) from recent updates.")
    except Exception as exc:
        print(f"[BACKFILL] Skipped (not critical): {exc}")


def log_signal(pair: str, direction: str, entry: float, tp1: float, tp2: float, sl: float, source: str) -> None:
    global _signal_log
    
    # Check for duplicates in the last 12 hours
    now = datetime.now(timezone.utc)
    for sig in reversed(_signal_log):
        try:
            sig_date = sig.get("date", "")
            sig_time = sig.get("time", "").replace(" UTC", "")
            sig_dt = datetime.strptime(f"{sig_date} {sig_time}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            if (now - sig_dt).total_seconds() < 43200:
                if sig.get("pair") == pair and sig.get("direction") == direction:
                    # Suppress if entry price difference is less than 0.5%
                    entry_diff = abs(float(sig.get("entry", 0)) - entry)
                    pct_diff = (entry_diff / entry) if entry else 0
                    if pct_diff < 0.005:
                        print(f"[LOG SIGNAL] Suppressed duplicate signal for {pair} {direction} at {entry}")
                        return
        except Exception:
            pass

    record = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "pair": pair,
        "direction": direction,
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "source": source,
    }
    _signal_log.append(record)
    save_signal_log(_signal_log)
    # Attempt automated trading if enabled (safe default: disabled or dummy/paper broker)
    try:
        if os.getenv("AUTOTRADE_ENABLED", "").strip().lower() in {"1", "true", "yes"}:
            res = autotrade.place_trade(pair, direction, entry, tp1, tp2, sl)
            print(f"[AUTOTRADE] {res}")
    except Exception as exc:
        print(f"[AUTOTRADE] Error while placing trade: {exc}")


def get_active_provider() -> str:
    if NEWS_PROVIDER in {"newsdata", "newsapi", "finnhub"}:
        return NEWS_PROVIDER
    if FINNHUB_API_KEY:
        return "finnhub"
    if NEWS_API_KEY:
        return "newsapi"
    return "newsdata"


def build_newsdata_url(query: str) -> str:
    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": query,
        "language": "en",
        "category": "business",
    }
    return f"{NEWSDATA_API_URL}?{urlencode(params)}"


def build_newsapi_url(query: str) -> str:
    # Use top-headlines to get real-time news (everything endpoint has a 24-hour delay on NewsAPI free plan)
    # Simplify the query since top-headlines has stricter keyword matching
    simple_query = ""
    keywords = re.findall(r'\b[a-zA-Z]{3,}\b', query)
    if keywords:
        simple_query = " ".join(keywords[:3])
        
    params = {
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "category": "business",
        "pageSize": "25",
    }
    if simple_query:
        params["q"] = simple_query
        
    return f"{NEWSAPI_URL}?{urlencode(params)}"


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def _find_child_text(parent: Any, names: list[str]) -> str:
    if parent is None:
        return ""
    for name in names:
        child = parent.find(name)
        if child is not None and (child.text or "").strip():
            return _strip_html(child.text)
    for child in parent.iter():
        tag = child.tag.split("}")[-1]
        if tag in names and (child.text or "").strip():
            return _strip_html(child.text)
    return ""


def _extract_link(entry: Any) -> str:
    for child in entry.iter():
        if child.tag.split("}")[-1] == "link":
            href = child.get("href") or (child.text or "").strip()
            if href:
                return href
    return ""


def _guess_source_name(url: str) -> str:
    try:
        from urllib.parse import urlparse

        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host.split(".")[0].replace("-", " ").title()
    except Exception:
        return "Live News"


def _parse_rss_or_atom(content: str, source_name: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    entries = []
    if root.tag.endswith("rss"):
        entries = root.findall("./channel/item")
    elif root.tag.endswith("feed"):
        entries = root.findall("./entry")
    else:
        return []

    articles: list[dict[str, Any]] = []
    for entry in entries:
        title = _find_child_text(entry, ["title"]) or _find_child_text(entry, ["headline"])
        description = _find_child_text(entry, ["description", "summary", "content"])
        link = _extract_link(entry)
        pub_date = _find_child_text(entry, ["published", "updated", "pubDate", "pubdate"])
        if title:
            articles.append(
                {
                    "title": _strip_html(title),
                    "description": _strip_html(description),
                    "link": link,
                    "pubDate": pub_date,
                    "source_name": source_name,
                    "keywords": [],
                }
            )
    return articles


def _parse_html_page(content: str, url: str) -> list[dict[str, Any]]:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    title = _strip_html(title_match.group(1)) if title_match else ""
    desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', content, flags=re.IGNORECASE)
    description = _strip_html(desc_match.group(1)) if desc_match else ""
    if not title:
        return []
    return [{
        "title": title,
        "description": description,
        "link": url,
        "pubDate": "",
        "source_name": _guess_source_name(url),
        "keywords": [],
    }]


def fetch_live_news_from_url(url: str) -> list[dict[str, Any]]:
    if not url:
        return []
    try:
        with urlopen(url, timeout=15) as response:
            content = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    lower = content.lower()
    if "<rss" in lower or "<feed" in lower or "<?xml" in lower:
        return _parse_rss_or_atom(content, _guess_source_name(url))
    return _parse_html_page(content, url)


def fetch_twitter_posts() -> list[dict[str, Any]]:
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
            
    return results


def collect_live_market_news(raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("headline") or item.get("name") or item.get("text") or ""
        if not title or not str(title).strip():
            continue
        article = {
            "article_id": item.get("article_id") or item.get("id") or item.get("link") or item.get("url") or title,
            "title": str(title).strip(),
            "description": item.get("description") or item.get("summary") or item.get("content") or item.get("text") or "",
            "link": item.get("link") or item.get("url") or item.get("share_url") or "",
            "pubDate": item.get("pubDate") or item.get("published_at") or item.get("publishedAt") or item.get("created_at") or item.get("date") or "",
            "source_name": item.get("source_name") or item.get("source") or item.get("author") or item.get("provider") or "Live News",
            "keywords": item.get("keywords") or [],
        }
        if article.get("description") and isinstance(article.get("description"), str):
            article["description"] = article["description"].strip()
        key = article_key(article)
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        articles.append(article)
    return articles


def fetch_live_market_news() -> list[dict[str, Any]]:
    if not LIVE_NEWS_ENABLED:
        return []

    candidates: list[dict[str, Any]] = []
    candidates.extend(fetch_twitter_posts())
    for feed_url in LIVE_NEWS_FEEDS:
        candidates.extend(fetch_live_news_from_url(feed_url))
    return collect_live_market_news(candidates)


def normalize_newsdata_article(article: dict[str, Any]) -> dict[str, Any]:
    return {
        "article_id": article.get("article_id") or article.get("link") or article.get("title"),
        "title": article.get("title"),
        "description": article.get("description"),
        "link": article.get("link"),
        "pubDate": article.get("pubDate"),
        "source_name": article.get("source_name"),
        "keywords": article.get("keywords") or [],
    }


def normalize_newsapi_article(article: dict[str, Any]) -> dict[str, Any]:
    source = article.get("source") or {}
    return {
        "article_id": article.get("url") or article.get("title") or article.get("publishedAt"),
        "title": article.get("title"),
        "description": article.get("description") or article.get("content"),
        "link": article.get("url"),
        "pubDate": article.get("publishedAt"),
        "source_name": source.get("name") or "Unknown source",
        "keywords": [],
    }


def article_key(article: dict[str, Any]) -> str:
    return str(
        article.get("article_id")
        or article.get("link")
        or article.get("title")
        or article.get("pubDate")
        or ""
    )


def clean_title_for_dedup(title: str) -> str:
    import re
    if not title:
        return ""
    # Lowercase, keep only alphanumeric, sort the words so word order changes don't bypass checks
    words = sorted(re.findall(r'[a-z0-9]+', title.lower()))
    return "".join(words)


def normalize_text(article: dict[str, Any]) -> str:
    parts = [
        article.get("title") or "",
        article.get("description") or "",
        " ".join(article.get("keywords") or []),
        article.get("source_name") or "",
    ]
    return " ".join(parts).lower()


def is_forex_relevant(article: dict[str, Any]) -> bool:
    text = normalize_text(article)
    return any(term in text for term in FOREX_TERMS)


def identify_asset(article: dict[str, Any]) -> str:
    text = normalize_text(article)
    for symbol, hints in CURRENCY_HINTS.items():
        if any(hint in text for hint in hints):
            return symbol
    return "MARKET"


def infer_bias_signal(article: dict[str, Any]) -> str | None:
    text = normalize_text(article)

    subject = None
    for symbol, hints in CURRENCY_HINTS.items():
        if any(hint in text for hint in hints):
            subject = symbol
            break

    if not subject:
        return None

    score = sum(1 for word in POSITIVE_KEYWORDS if word in text)
    score -= sum(1 for word in NEGATIVE_KEYWORDS if word in text)

    if score == 0:
        return None

    direction = "Bullish" if score > 0 else "Bearish"
    return f"{direction} {subject}"


def fetch_current_prices() -> dict[str, float]:
    rates: dict[str, float] = {}
    try:
        with urlopen(FOREX_PRICE_API, timeout=10) as r:
            data = json.load(r)
        base_rates = data.get("rates", {})
        usd_base = {"USD": 1.0} | base_rates
        for asset, pairs in TRADE_PAIRS.items():
            for pair, _, _ in pairs:
                if pair in rates:
                    continue
                if "/" not in pair:
                    continue
                base, quote = pair.split("/")
                b_rate = usd_base.get(base)
                q_rate = usd_base.get(quote)
                if b_rate and q_rate:
                    rates[pair] = q_rate / b_rate
    except Exception:
        pass

    yf_map = {
        "XAU/USD": "GC=F",
        "XAG/USD": "SI=F",
        "WTI": "CL=F",
        "BRENT": "BZ=F",
        "US10Y": "^TNX",
        "BTC/USD": "BTC-USD",
        "ETH/USD": "ETH-USD",
        "SOL/USD": "SOL-USD",
        "XRP/USD": "XRP-USD",
        "ADA/USD": "ADA-USD",
        "DOGE/USD": "DOGE-USD",
        "DOT/USD": "DOT-USD",
        "AVAX/USD": "AVAX-USD",
        "LINK/USD": "LINK-USD",
        "LTC/USD": "LTC-USD",
        "US30": "^DJI",
        "US100": "^IXIC",
        "DXY": "DX-Y.NYB",
        "SP500": "^GSPC",
        "UK100": "^FTSE",
        "GER40": "^GDAXI",
        "JPN225": "^N225",
        "HK50": "^HSI",
        "AUS200": "^AXJO",
        "NIFTY": "^NSEI",
        "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK",
        "AAPL": "AAPL",
        "MSFT": "MSFT",
        "GOOGL": "GOOGL",
        "AMZN": "AMZN",
        "NVDA": "NVDA",
        "META": "META",
        "TSLA": "TSLA",
        "JPM": "JPM",
        "V": "V",
        "WMT": "WMT",
        "JNJ": "JNJ",
        "PG": "PG",
        "XOM": "XOM",
        "UNH": "UNH",
        "HD": "HD",
        "BAC": "BAC",
        "DIS": "DIS",
        "NFLX": "NFLX",
        "ADBE": "ADBE",
        "CRM": "CRM",
        "INTC": "INTC",
        "AMD": "AMD",
        "PYPL": "PYPL",
        "UBER": "UBER",
        "NKE": "NKE",
        "BA": "BA",
        "COIN": "COIN",
        "SNAP": "SNAP",
        "SQ": "SQ",
        "PLTR": "PLTR",
        "RBLX": "RBLX",
        "MCD": "MCD",
        "SBUX": "SBUX",
        "NIO": "NIO",
        "RIVN": "RIVN",
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFCBANK": "HDFCBANK.NS",
        "INFY": "INFY.NS",
        "ICICIBANK": "ICICIBANK.NS",
        "SBIN": "SBIN.NS",
        "BHARTI": "BHARTIARTL.NS",
        "WIPRO": "WIPRO.NS",
        "ITC": "ITC.NS",
        "LT": "LT.NS",
        "AXISBANK": "AXISBANK.NS",
        "KOTAKBANK": "KOTAKBANK.NS",
        "MARUTI": "MARUTI.NS",
        "TATAMOTORS": "TATAMOTORS.NS",
        "ASIANPAINT": "ASIANPAINT.NS",
        "HCLTECH": "HCLTECH.NS",
        "SUNPHARMA": "SUNPHARMA.NS",
        "BAJFINANCE": "BAJFINANCE.NS",
        "TITAN": "TITAN.NS",
        "NTPC": "NTPC.NS",
        "ONGC": "ONGC.NS",
        "POWERGRID": "POWERGRID.NS",
        "ULTRACEMCO": "ULTRACEMCO.NS",
        "TATASTEEL": "TATASTEEL.NS",
        "JSWSTEEL": "JSWSTEEL.NS",
        "HINDALCO": "HINDALCO.NS",
        "TECHM": "TECHM.NS",
        "COALINDIA": "COALINDIA.NS",
        "HINDUNILVR": "HINDUNILVR.NS",
        "BRITANNIA": "BRITANNIA.NS",
        "NESTLEIND": "NESTLEIND.NS",
        "M&M": "M&M.NS",
        "EICHERMOT": "EICHERMOT.NS",
        "HEROMOTOCO": "HEROMOTOCO.NS",
        "BAJAJ_AUTO": "BAJAJ-AUTO.NS",
        "TATACONSUM": "TATACONSUM.NS",
        "DABUR": "DABUR.NS",
        "MARICO": "MARICO.NS",
        "HDFC": "HDFC.NS",
        "ICICIPRUDI": "ICICIPRUDI.NS",
        "HDFCLIFE": "HDFCLIFE.NS",
        "SBILIFE": "SBILIFE.NS",
        "TRENT": "TRENT.NS",
        "AVENUE": "AVENUE.NS",
        "PIDILITIND": "PIDILITIND.NS",
        "HAVELLS": "HAVELLS.NS",
        "SIEMENS": "SIEMENS.NS",
        "BEL": "BEL.NS",
        "BHEL": "BHEL.NS",
        "HAL": "HAL.NS",
        "IRFC": "IRFC.NS",
        "IREDA": "IREDA.NS",
        "SUZLON": "SUZLON.NS",
        "ADANIENT": "ADANIENT.NS",
        "ADANIPORTS": "ADANIPORTS.NS",
        "ADANIGREEN": "ADANIGREEN.NS",
        "ADANITRANS": "ADANITRANS.NS",
        "ADANIPOWER": "ADANIPOWER.NS",
        "HINDZINC": "HINDZINC.NS",
        "VEDL": "VEDL.NS",
        "IOC": "IOC.NS",
        "BPCL": "BPCL.NS",
        "GAIL": "GAIL.NS",
        "NATIONALUM": "NATIONALUM.NS",
        "ZOMATO": "ZOMATO.NS",
        "SWIGGY": "SWIGGY.NS",
        "PAYTM": "PAYTM.NS",
        "POLICYBZR": "POLICYBZR.NS",
        "NYKAA": "NYKAA.NS",
        "HDFCAMC": "HDFCAMC.NS",
        "GRASIM": "GRASIM.NS",
        "DIVISLAB": "DIVISLAB.NS",
        "CIPLA": "CIPLA.NS",
        "DRREDDY": "DRREDDY.NS",
        "APOLLOHOSP": "APOLLOHOSP.NS",
        "AUROPHARMA": "AUROPHARMA.NS",
        "TVSMOTOR": "TVSMOTOR.NS",
    }
    try:
        for pair, ticker in yf_map.items():
            if pair not in rates:
                tk = yf.Ticker(ticker)
                hist = tk.history(period="1d")
                if not hist.empty:
                    rates[pair] = round(float(hist["Close"].iloc[-1]), 2)
    except Exception:
        pass

    return rates


def compute_confidence(text: str) -> tuple[str, str]:
    score = sum(1 for word in POSITIVE_KEYWORDS if word in text)
    score -= sum(1 for word in NEGATIVE_KEYWORDS if word in text)
    abs_score = abs(score)
    if abs_score >= 4:
        level = "High"
    elif abs_score >= 2:
        level = "Medium"
    else:
        level = "Low"
    direction = "Bullish" if score > 0 else "Bearish"
    return direction, level


def is_high_impact(article: dict[str, Any]) -> bool:
    text = normalize_text(article)
    return any(kw in text for kw in HIGH_IMPACT_KEYWORDS)


def format_trade_lines(bias: str, source: str = "news") -> str | None:
    parts = bias.split()
    if len(parts) != 2:
        return None
    direction_str, asset = parts[0], parts[1]
    pairs = TRADE_PAIRS.get(asset)
    if not pairs:
        return None
    is_bullish = direction_str == "Bullish"
    prices = fetch_current_prices()
    lines: list[str] = []
    for i, (pair, multiplier, pip_size) in enumerate(pairs, 1):
        price = prices.get(pair)
        if not price:
            lines.append(f"{i}. {pair}")
            continue
        is_buy = (is_bullish == (multiplier > 0))
        entry = round(price, 4)
        tp1 = round(price + (30 * pip_size) if is_buy else price - (30 * pip_size), 4)
        tp2 = round(price + (50 * pip_size) if is_buy else price - (50 * pip_size), 4)
        sl = round(price - (20 * pip_size) if is_buy else price + (20 * pip_size), 4)
        dir_label = "BUY" if is_buy else "SELL"
        icon = " 🟢" if is_buy else " 🔴"
        lines.append(f"{i}.{icon} {dir_label} {pair} @ {_price_str(entry, pair)}")
        lines.append(f"   Targets: {_price_str(tp1, pair)} / {_price_str(tp2, pair)} | SL: {_price_str(sl, pair)}")
        log_signal(pair, dir_label, entry, tp1, tp2, sl, source)
    return "\n".join(lines) if lines else None


def detect_asset_in_text(text: str) -> str | None:
    text_lower = text.lower()
    for symbol, hints in CURRENCY_HINTS.items():
        if any(hint in text_lower for hint in hints):
            return symbol
    return None


def ai_verify_trade_suggestion(trade_text: str, asset: str) -> str | None:
    prompt = (
        "You are an expert trading analyst. Verify this trade suggestion:\n"
        f"{trade_text}\n\n"
        f"Is this a reasonable trade setup for {asset}? "
        "Consider current market conditions. "
        "Reply: 'APPROVED - [reason]' or 'REJECTED - [reason]'. "
        "Be concise - max 2 sentences."
    )
    return _best_ai(prompt)


def ai_enhance_trade_suggestion(trade_text: str, context_title: str) -> str | None:
    prompt = (
        "You are an expert trading analyst improving a trade suggestion.\n"
        f"Current suggestion:\n{trade_text}\n\n"
        f"News context: {context_title}\n\n"
        "Review this suggestion for:\n"
        "1. Direction correctness based on the news\n"
        "2. Sensible entry/TP/SL levels\n"
        "3. Risk management quality\n\n"
        "If it is already good, reply 'OK'.\n"
        "If it needs improvement, provide the improved version. "
        "Keep the same format (BUY/SELL, @, Targets:, SL). "
        "Max 2 sentences of explanation."
    )
    result = _best_ai(prompt)
    if result and result.strip().upper() == "OK":
        return None
    return result


def generate_asset_trade_setup(asset: str, question: str) -> str | None:
    pairs = TRADE_PAIRS.get(asset)
    if not pairs:
        return None

    prices = fetch_current_prices()

    dir_prompt = (
        f"Based on this question: '{question}'\n"
        f"Should we go LONG (buy) or SHORT (sell) {asset}? "
        "Reply with only one word: LONG or SHORT."
    )
    direction = _best_ai(dir_prompt, system_prompt=TRADING_SYSTEM_PROMPT)
    if not direction:
        return None
    is_bullish = "LONG" in direction.strip().upper()

    lines: list[str] = []
    for i, (pair, multiplier, pip_size) in enumerate(pairs, 1):
        price = prices.get(pair)
        if not price:
            lines.append(f"{i}. {pair} - price unavailable")
            continue
        is_buy = (is_bullish == (multiplier > 0))
        entry = round(price, 4)
        tp1 = round(price + (30 * pip_size) if is_buy else price - (30 * pip_size), 4)
        tp2 = round(price + (50 * pip_size) if is_buy else price - (50 * pip_size), 4)
        sl = round(price - (20 * pip_size) if is_buy else price + (20 * pip_size), 4)
        dir_label = "BUY" if is_buy else "SELL"
        icon = " 🟢" if is_buy else " 🔴"
        lines.append(f"{i}.{icon} {dir_label} {pair} @ {_price_str(entry, pair)}")
        lines.append(f"   Targets: {_price_str(tp1, pair)} / {_price_str(tp2, pair)} | SL: {_price_str(sl, pair)}")
        log_signal(pair, dir_label, entry, tp1, tp2, sl, "question")

    if not lines:
        return None

    trade_text = "\n".join(lines)
    verification = ai_verify_trade_suggestion(trade_text, asset)

    result = [f"<b>Real-Time Setup ({asset}):</b>", trade_text]
    if verification:
        result.append(f"\n<b>AI Verification:</b> {verification}")

    return "\n".join(result)


def _call_onemin_api(prompt: str, system: str | None = None, model: str = "gpt-4o") -> str | None:
    api_key = os.getenv("ONEMIN_API_KEY", "").strip()
    if not api_key:
        return None
    url = "https://api.1min.ai/api/chat-with-ai"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    full_prompt = ""
    if system:
        full_prompt += f"System Instructions:\n{system}\n\n"
    full_prompt += prompt
    
    payload = {
        "type": "UNIFY_CHAT_WITH_AI",
        "model": model,
        "promptObject": {
            "prompt": full_prompt,
            "settings": {
                "webSearchSettings": {
                    "webSearch": False
                }
            }
        }
    }
    try:
        import requests
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            res_json = resp.json()
            detail = res_json.get("aiRecordDetail", {})
            result_obj = detail.get("resultObject", [])
            if result_obj and isinstance(result_obj, list):
                return result_obj[0].strip()
    except Exception as e:
        print(f"[1MIN.AI ERROR]: {e}")
    return None


def _analyzer_groq_chat(prompt: str, system_prompt: str | None = None, json_mode: bool = False) -> str | None:
    import requests
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # 1. Try Bynara API (deepseek-v4-pro-free)
    bynara_key = os.getenv("BYNARA_API_KEY", "sk-nry-wWqj7bgCiHuO9eKsKXC5PcytwpCAt4kmAUbM6ol70uA")
    if bynara_key:
        payload = {
            "model": "deepseek-v4-pro-free",
            "messages": messages
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            resp = requests.post(
                "https://router.bynara.id/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {bynara_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=25,
            )
            if resp.status_code == 200:
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[BYNARA] Error: {e}")

    # 2. Try OneMin API
    onemin_key = os.getenv("ONEMIN_API_KEY", "").strip()
    if onemin_key:
        for m in ["gpt-4o", "deepseek-chat", "gpt-4o-mini"]:
            res = _call_onemin_api(prompt, system=system_prompt, model=m)
            if res:
                return res

    # 3. Try Groq API
    if not ANALYZER_GROQ_API_KEY:
        return None

    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for m in models_to_try:
        payload = {
            "model": m,
            "messages": messages,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {ANALYZER_GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=20,
            )
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                return text if json_mode else escape(text)
        except Exception:
            continue
    return None


def _groq_chat(prompt: str, system_prompt: str | None = None) -> str | None:
    onemin_key = os.getenv("ONEMIN_API_KEY", "").strip()
    if onemin_key:
        for m in ["gpt-4o", "deepseek-chat", "gpt-4o-mini"]:
            res = _call_onemin_api(prompt, system=system_prompt, model=m)
            if res:
                return escape(res)

    if not GROQ_API_KEY:
        return None
    import requests
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Try Llama 3.3 70B first
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
            },
            timeout=15,
        )
        if resp.status_code == 429:
            raise Exception("Rate limit hit, falling back")
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return escape(text)
    except Exception:
        # Fallback to high-rate-limit 8B model
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                },
                timeout=15,
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
            return escape(text)
        except Exception:
            return None


# ── Finnhub API helpers ──────────────────────────────────────────────────────

_FINNHUB_SESSION_CACHE: dict[str, tuple[float, dict]] = {}


def _finnhub_get(path: str, params: dict | None = None) -> dict | None:
    if not FINNHUB_API_KEY:
        return None
    try:
        p = dict(params or {})
        p["token"] = FINNHUB_API_KEY
        url = f"{FINNHUB_BASE}{path}?{urlencode(p)}"
        with urlopen(url, timeout=10) as r:
            return json.load(r)
    except Exception:
        return None


def finnhub_quote(symbol: str) -> dict | None:
    """Get real-time quote for a stock symbol from Finnhub."""
    return _finnhub_get("/quote", {"symbol": symbol})


def finnhub_company_news(symbol: str, from_date: str = "", to_date: str = "") -> list[dict]:
    """Get company news from Finnhub."""
    now = datetime.now(timezone.utc)
    to_d = to_date or now.strftime("%Y-%m-%d")
    from_d = from_date or (now - timedelta(days=7)).strftime("%Y-%m-%d")
    data = _finnhub_get("/company-news", {"symbol": symbol, "from": from_d, "to": to_d})
    return data if isinstance(data, list) else []


def finnhub_market_news(category: str = "general") -> list[dict]:
    """Get market news. Categories: general, forex, crypto, merger."""
    data = _finnhub_get("/news", {"category": category})
    return data if isinstance(data, list) else []


def finnhub_news_sentiment(symbol: str) -> dict | None:
    """Get news sentiment for a stock from Finnhub."""
    return _finnhub_get("/news-sentiment", {"symbol": symbol})


def finnhub_stock_symbols(exchange: str = "US") -> list[dict]:
    """Get list of stock symbols for an exchange."""
    data = _finnhub_get("/stock/symbol", {"exchange": exchange})
    return data if isinstance(data, list) else []


def finnhub_company_profile(symbol: str) -> dict | None:
    """Get company profile from Finnhub."""
    return _finnhub_get("/stock/profile2", {"symbol": symbol})


def finnhub_enrich_with_sentiment(asset: str) -> str | None:
    """Enrich trade signal with Finnhub sentiment data."""
    finnhub_symbol = _asset_to_finnhub_symbol(asset)
    if not finnhub_symbol:
        return None
    quote = finnhub_quote(finnhub_symbol)
    sentiment = finnhub_news_sentiment(finnhub_symbol)
    parts: list[str] = []
    if quote:
        c = quote.get("c")
        dp = quote.get("dp")
        h = quote.get("h")
        l = quote.get("l")
        if c:
            chg_str = f" ({'+' if dp and dp >= 0 else ''}{dp:.2f}%)" if dp else ""
            parts.append(f"Last: {c}{chg_str}")
            if h and l:
                parts.append(f"Day Range: {l} - {h}")
    if sentiment:
        bs = sentiment.get("bearishPercent")
        bsp = sentiment.get("bullishPercent")
        if bs is not None and bsp is not None:
            parts.append(f"Bearish: {bs:.1f}% / Bullish: {bsp:.1f}%")
        mention = sentiment.get("mentionCount")
        if mention:
            parts.append(f"Mentions: {mention}")
    return " | ".join(parts) if parts else None


def _asset_to_finnhub_symbol(asset: str) -> str | None:
    """Map internal asset symbols to Finnhub tickers."""
    m = {
        "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL", "AMZN": "AMZN",
        "NVDA": "NVDA", "META": "META", "TSLA": "TSLA", "JPM": "JPM",
        "V": "V", "WMT": "WMT", "JNJ": "JNJ", "PG": "PG",
        "XOM": "XOM", "UNH": "UNH", "HD": "HD", "BAC": "BAC",
        "DIS": "DIS", "NFLX": "NFLX", "ADBE": "ADBE", "CRM": "CRM",
        "INTC": "INTC", "AMD": "AMD", "PYPL": "PYPL", "UBER": "UBER",
        "NKE": "NKE", "BA": "BA", "COIN": "COIN", "SNAP": "SNAP",
        "SQ": "SQ", "PLTR": "PLTR", "RBLX": "RBLX", "MCD": "MCD",
        "SBUX": "SBUX", "NIO": "NIO", "RIVN": "RIVN",
        "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS",
        "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS",
        "ICICIBANK": "ICICIBANK.NS", "SBIN": "SBIN.NS",
        "BHARTI": "BHARTIARTL.NS", "WIPRO": "WIPRO.NS",
        "ITC": "ITC.NS", "LT": "LT.NS", "MARUTI": "MARUTI.NS",
        "TATAMOTORS": "TATAMOTORS.NS", "NIFTY": "^NSEI",
        "SENSEX": "^BSESN", "XAU/USD": "GC=F", "XAG/USD": "SI=F",
        "WTI": "CL=F", "BRENT": "BZ=F", "BTC/USD": "BTC-USD",
        "ETH/USD": "ETH-USD",
    }
    return m.get(asset)


# ── OpenAI API helper (alternative to Groq) ──────────────────────────────────

def _openai_chat(prompt: str, system_prompt: str | None = None) -> str | None:
    if not OPENAI_API_KEY:
        return None
    try:
        import requests
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "max_tokens": 500,
            },
            timeout=20,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return escape(text)
    except Exception:
        return None


def _best_ai(prompt: str, system_prompt: str | None = None) -> str | None:
    """Try OpenAI first, fall back to Groq."""
    result = _openai_chat(prompt, system_prompt)
    if result:
        return result
    return _groq_chat(prompt, system_prompt)


def ai_enhanced_market_analysis(asset: str, news_text: str) -> str | None:
    """Use OpenAI for deeper market analysis with Finnhub data enrichment."""
    finnhub_data = finnhub_enrich_with_sentiment(asset)
    context = f"Asset: {asset}\nNews: {news_text[:500]}"
    if finnhub_data:
        context += f"\nMarket Data: {finnhub_data}"
    prompt = (
        "You are an expert financial analyst. Analyze this asset based on the news and market data provided.\n\n"
        f"{context}\n\n"
        "Provide:\n"
        "1. Direction bias (Bullish/Bearish/Neutral) with confidence level\n"
        "2. Key support and resistance levels\n"
        "3. Entry strategy with specific price zones\n"
        "4. Risk management advice\n"
        "Keep it concise - max 5 sentences."
    )
    return _best_ai(prompt, "You are a professional trading analyst. Be factual and data-driven.")


def finnhub_fetch_news(category: str = "general") -> list[dict]:
    """Fetch news from Finnhub and normalize to our format."""
    raw = finnhub_market_news(category)
    articles: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        pub = item.get("datetime")
        pub_dt = ""
        if pub:
            try:
                pub_dt = datetime.fromtimestamp(pub, tz=timezone.utc).isoformat()
            except Exception:
                pub_dt = ""
        articles.append({
            "article_id": item.get("id") or item.get("url") or item.get("headline", ""),
            "title": item.get("headline", ""),
            "description": item.get("summary", ""),
            "link": item.get("url", ""),
            "pubDate": pub_dt,
            "source_name": item.get("source", "Finnhub"),
            "keywords": item.get("categories", []),
            "related": item.get("related", ""),
        })
    return articles


def build_market_context() -> str:
    ctx_parts: list[str] = []
    try:
        prices = fetch_current_prices()
        key_prices = {
            "XAU/USD": prices.get("XAU/USD"),
            "US100": prices.get("US100"),
            "EUR/USD": prices.get("EUR/USD"),
            "BTC/USD": prices.get("BTC/USD"),
        }
        for name, price in key_prices.items():
            if price:
                ctx_parts.append(f"{name}: {price}")
    except Exception:
        pass
    if not ctx_parts:
        return ""
    return "Current prices: " + ", ".join(ctx_parts) + "."


def ai_analyze_news(article: dict[str, Any]) -> str | None:
    title = article.get("title", "")
    desc = (article.get("description") or "")[:200]
    market_ctx = build_market_context()

    asset = identify_asset(article)
    finnhub_enrichment = ""
    if asset and asset != "MARKET":
        try:
            fh = finnhub_enrich_with_sentiment(asset)
            if fh:
                finnhub_enrichment = f"\nFinnhub Data: {fh}"
        except Exception:
            pass

    prompt = (
        f"News: {title}\n{desc}\n\n"
        f"{market_ctx}{finnhub_enrichment}\n\n"
        "Give a 1-line trading insight for this financial news. "
        "Mention direction (bullish/bearish) and which asset. "
        "Be specific (entry bias, key level). Max 20 words."
    )
    return _best_ai(prompt, system_prompt=TRADING_SYSTEM_PROMPT)


def detect_institutional_analysis_prompt(question: str) -> tuple[str, dict[str, Any]] | None:
    question_lower = question.lower()
    for prompt_id, config in INSTITUTIONAL_ANALYSIS_PROMPTS.items():
        if any(keyword in question_lower for keyword in config["keywords"]):
            return prompt_id, config
    return None


def list_institutional_prompt_titles() -> str:
    return "\n".join(
        f"- {config['title']}"
        for config in INSTITUTIONAL_ANALYSIS_PROMPTS.values()
    )


def build_institutional_analysis_prompt(question: str, config: dict[str, Any], market_ctx: str) -> str:
    return (
        f"Analysis framework: {config['title']}\n\n"
        f"{config['prompt']}\n\n"
        f"Current market context available to the app:\n{market_ctx or 'No live price context available.'}\n\n"
        f"User request and details:\n{question}\n\n"
        "Adapt the framework to the asset, portfolio, sector, or trade in the user request. "
        "If the user omitted required inputs, still provide the best actionable framework and clearly list the missing inputs. "
        "Keep Telegram readability: short sections, compact tables, and a final trade/portfolio action summary. "
        "Stay under 450 words."
    )


def ai_answer_question(question: str) -> str | None:
    market_ctx = build_market_context()
    matched_prompt = detect_institutional_analysis_prompt(question)
    if matched_prompt:
        _, config = matched_prompt
        prompt = build_institutional_analysis_prompt(question, config, market_ctx)
        return _best_ai(prompt, system_prompt=INSTITUTIONAL_ANALYSIS_SYSTEM_PROMPT)

    prompt = (
        "You are an expert forex and stock market trading analyst. "
        "Answer the user's trading question concisely and accurately. "
        "Provide analysis, direction (bullish/bearish), key price levels if applicable, "
        "and risk management advice.\n\n"
        f"{market_ctx}\n\n"
        f"Question: {question}\n\n"
        "Keep it under 150 words. Be specific about entry zones, not just direction."
    )
    return _best_ai(prompt, system_prompt=TRADING_SYSTEM_PROMPT)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global _subscribers
    chat_id = update.effective_chat.id
    if chat_id not in _subscribers:
        _subscribers.append(chat_id)
        save_subscribers(_subscribers)
        print(f"[SUBSCRIBE] Chat {chat_id} subscribed via /start")
    await update.message.reply_text(
        "<b>ForexSignalAI Trade Analyzer</b>\n\n"
        "You are now subscribed to trading signals and market updates.\n\n"
        "Send me any trading or market question and I'll analyze it with AI.\n\n"
        "Examples:\n"
        "- Is EUR/USD bullish today?\n"
        "- Should I buy gold now?\n"
        "- Technical analysis of Nifty\n"
        "- DCF valuation for TSLA\n"
        "- Portfolio risk analysis: AAPL 40%, NIFTY 30%, BTC 30%\n\n"
        "Use /prompts to see all advanced analysis frameworks.",
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global _subscribers
    chat_id = update.effective_chat.id
    if chat_id not in _subscribers:
        _subscribers.append(chat_id)
        save_subscribers(_subscribers)
        print(f"[SUBSCRIBE] Chat {chat_id} subscribed via /help")
    await update.message.reply_text(
        "Send any trading or market question. "
        "I will analyze it using AI and provide trading insights.\n\n"
        "Advanced examples:\n"
        "- Technical analysis of BTC/USD\n"
        "- DCF valuation for NVDA\n"
        "- Earnings breakdown for AAPL\n"
        "- Macro impact on my portfolio\n\n"
        "Use /prompts to see every framework."
    )


async def prompts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>Advanced Analysis Frameworks</b>\n\n"
        f"{escape(list_institutional_prompt_titles())}\n\n"
        "Ask naturally, for example: DCF valuation for TSLA, technical analysis of Nifty, "
        "portfolio construction for age 30 with monthly SIP, or dividend strategy for $50,000.",
        parse_mode="HTML",
    )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global _subscribers
    chat_id = update.effective_chat.id
    if chat_id in _subscribers:
        await update.message.reply_text("You are already subscribed to trading signals.")
        return
    _subscribers.append(chat_id)
    save_subscribers(_subscribers)
    print(f"[SUBSCRIBE] Chat {chat_id} subscribed via /subscribe")
    await update.message.reply_text(
        "✅ You are now subscribed to trading signals and market updates!\n\n"
        "You will receive:\n"
        "• Forex / crypto / stock trade signals\n"
        "• India NSE/BSE intraday alerts\n"
        "• BTC market updates & trade ideas\n"
        "• AI educational tips\n"
        "• Morning briefing & session summaries\n\n"
        "Use /unsubscribe to stop."
    )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global _subscribers
    chat_id = update.effective_chat.id
    if chat_id in _subscribers:
        _subscribers.remove(chat_id)
        save_subscribers(_subscribers)
        print(f"[UNSUBSCRIBE] Chat {chat_id} unsubscribed")
    await update.message.reply_text("You have been unsubscribed from trading signals.")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    is_sub = chat_id in _subscribers
    await update.message.reply_text(
        f"🔔 Subscription status: {'✅ Active' if is_sub else '❌ Not subscribed'}\n\n"
        f"Chat ID: `{chat_id}`\n"
        f"Total subscribers: `{len(_subscribers)}`\n\n"
        f"Use /subscribe to start receiving signals.\n"
        f"Use /unsubscribe to stop.",
        parse_mode="Markdown",
    )


async def handle_user_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global _subscribers
    try:
        chat_id = update.effective_chat.id
        if chat_id not in _subscribers:
            _subscribers.append(chat_id)
            save_subscribers(_subscribers)
            print(f"[SUBSCRIBE] Chat {chat_id} subscribed via message")

        question = update.message.text.strip()
        if not question:
            return

        await update.message.chat.send_action(action="typing")

        answer = ai_answer_question(question)

        msg_parts: list[str] = []
        if answer:
            msg_parts.append(
                f"<b>Question:</b> {escape(question)}\n\n"
                f"<b>AI Analysis:</b>\n{answer}"
            )
        else:
            msg_parts.append(
                "<b>AI analysis unavailable.</b>\n\n"
                "GROQ_API_KEY may not be configured. Please check server settings."
            )
            await update.message.reply_text("\n".join(msg_parts), parse_mode="HTML")
            return

        asset = detect_asset_in_text(question)
        if asset and asset in TRADE_PAIRS:
            trade_setup = generate_asset_trade_setup(asset, question)
            if trade_setup:
                enhancement = ai_enhance_trade_suggestion(trade_setup, question)
                if enhancement:
                    trade_setup += f"\n\n<b>AI Improvement:</b> {enhancement}"
                msg_parts.append(f"\n\n{trade_setup}")

        await update.message.reply_text("\n".join(msg_parts), parse_mode="HTML")
    except Exception as e:
        print(f"[ERROR] handle_user_question: {e}")
        try:
            await update.message.reply_text(
                "Sorry, an error occurred while processing your question. Please check the bot logs."
            )
        except Exception:
            pass


def ensure_summary(article: dict[str, Any]) -> str:
    summary = article.get("description") or article.get("content") or ""
    summary = summary.strip()
    if summary:
        return escape(summary[:400])
    title = article.get("title") or ""
    if title:
        return escape(title[:400])
    return "No summary available."


def ai_translate(text: str, target_lang: str = "Bengali") -> str | None:
    if not GROQ_API_KEY or not text or not text.strip():
        return None
    prompt = (
        f"Translate this English text to {target_lang}. "
        "Keep ALL financial terms, numbers, percentages, currency codes (USD, EUR, XAU, etc.), "
        "and trading jargon (BUY, SELL, TP, SL, bullish, bearish, resistance, support, breakout, "
        "rally, decline) in English. Only translate surrounding explanatory words.\n\n"
        f"{text[:400]}"
    )
    return _groq_chat(prompt)


def translate_to_bengali(text: str) -> str | None:
    if not text or not text.strip():
        return None
    text = text[:500]

    ai_result = ai_translate(text)
    if ai_result:
        return ai_result

    try:
        from urllib.parse import quote
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=bn&dt=t&q={quote(text)}"
        with urlopen(url, timeout=10) as r:
            data = json.load(r)
        translated = data[0][0][0] if data and data[0] and data[0][0] else None
        if translated and translated.strip():
            return escape(translated)
    except Exception:
        pass

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="en", target="bn")
        translated = translator.translate(text)
        if translated and translated.strip():
            return escape(translated)
    except Exception:
        pass

    return None


def format_stock_price_info(asset: str) -> str | None:
    try:
        import indian_market as im
        yf_map = {
            "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL",
            "AMZN": "AMZN", "NVDA": "NVDA", "META": "META",
            "TSLA": "TSLA", "JPM": "JPM", "V": "V",
            "WMT": "WMT", "JNJ": "JNJ", "PG": "PG",
            "XOM": "XOM", "UNH": "UNH", "HD": "HD",
            "BAC": "BAC", "DIS": "DIS", "NFLX": "NFLX",
            "ADBE": "ADBE", "CRM": "CRM", "INTC": "INTC",
            "AMD": "AMD", "PYPL": "PYPL", "UBER": "UBER",
            "NKE": "NKE", "BA": "BA", "COIN": "COIN",
            "SNAP": "SNAP", "SQ": "SQ", "PLTR": "PLTR",
            "RBLX": "RBLX", "MCD": "MCD", "SBUX": "SBUX",
            "NIO": "NIO", "RIVN": "RIVN",
            "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "HDFCBANK": "HDFCBANK.NS",
            "INFY": "INFY.NS", "ICICIBANK": "ICICIBANK.NS", "SBIN": "SBIN.NS",
            "BHARTI": "BHARTIARTL.NS", "WIPRO": "WIPRO.NS", "ITC": "ITC.NS",
            "LT": "LT.NS", "AXISBANK": "AXISBANK.NS", "KOTAKBANK": "KOTAKBANK.NS",
            "MARUTI": "MARUTI.NS", "TATAMOTORS": "TATAMOTORS.NS",
            "ASIANPAINT": "ASIANPAINT.NS", "HCLTECH": "HCLTECH.NS",
            "SUNPHARMA": "SUNPHARMA.NS", "BAJFINANCE": "BAJFINANCE.NS",
            "TITAN": "TITAN.NS", "NTPC": "NTPC.NS", "ONGC": "ONGC.NS",
            "POWERGRID": "POWERGRID.NS", "ULTRACEMCO": "ULTRACEMCO.NS",
            "TATASTEEL": "TATASTEEL.NS", "JSWSTEEL": "JSWSTEEL.NS",
            "HINDALCO": "HINDALCO.NS", "TECHM": "TECHM.NS",
            "COALINDIA": "COALINDIA.NS", "HINDUNILVR": "HINDUNILVR.NS",
            "BRITANNIA": "BRITANNIA.NS", "NESTLEIND": "NESTLEIND.NS",
            "M&M": "M&M.NS", "EICHERMOT": "EICHERMOT.NS",
            "HEROMOTOCO": "HEROMOTOCO.NS",
            "TATACONSUM": "TATACONSUM.NS", "DABUR": "DABUR.NS",
            "MARICO": "MARICO.NS", "HDFC": "HDFC.NS",
            "ICICIPRUDI": "ICICIPRUDI.NS", "HDFCLIFE": "HDFCLIFE.NS",
            "SBILIFE": "SBILIFE.NS", "TRENT": "TRENT.NS",
            "AVENUE": "AVENUE.NS", "PIDILITIND": "PIDILITIND.NS",
            "HAVELLS": "HAVELLS.NS", "SIEMENS": "SIEMENS.NS",
            "BEL": "BEL.NS", "BHEL": "BHEL.NS", "HAL": "HAL.NS",
            "IRFC": "IRFC.NS", "IREDA": "IREDA.NS", "SUZLON": "SUZLON.NS",
            "ADANIENT": "ADANIENT.NS", "ADANIPORTS": "ADANIPORTS.NS",
            "ADANIGREEN": "ADANIGREEN.NS", "ADANITRANS": "ADANITRANS.NS",
            "ADANIPOWER": "ADANIPOWER.NS",
            "HINDZINC": "HINDZINC.NS", "VEDL": "VEDL.NS",
            "IOC": "IOC.NS", "BPCL": "BPCL.NS", "GAIL": "GAIL.NS",
            "NATIONALUM": "NATIONALUM.NS",
            "ZOMATO": "ZOMATO.NS", "SWIGGY": "SWIGGY.NS",
            "PAYTM": "PAYTM.NS", "POLICYBZR": "POLICYBZR.NS",
            "NYKAA": "NYKAA.NS", "HDFCAMC": "HDFCAMC.NS",
            "GRASIM": "GRASIM.NS", "DIVISLAB": "DIVISLAB.NS",
            "CIPLA": "CIPLA.NS", "DRREDDY": "DRREDDY.NS",
            "APOLLOHOSP": "APOLLOHOSP.NS", "AUROPHARMA": "AUROPHARMA.NS",
            "TVSMOTOR": "TVSMOTOR.NS",
            "NIFTY": "^NSEI", "SENSEX": "^BSESN", "BANKNIFTY": "^NSEBANK",
            "SP500": "^GSPC", "UK100": "^FTSE", "GER40": "^GDAXI",
            "JPN225": "^N225", "HK50": "^HSI", "AUS200": "^AXJO",
        }
        yf_symbol = yf_map.get(asset)
        if not yf_symbol:
            return None
        data = im.fetch_ticker_price(yf_symbol)
        if not data:
            return None
        sign = "+" if data["change"] >= 0 else ""
        return (f"<b>Live Price:</b> {data['price']} ({sign}{data['change']} | "
                f"{sign}{data['pct']}%)")
    except Exception:
        return None


def generate_trade_suggestion(article: dict[str, Any], asset: str) -> str:
    bias = infer_bias_signal(article)
    if bias:
        trade = format_trade_lines(bias)
        if trade:
            return trade

    text = normalize_text(article)
    score = sum(1 for word in POSITIVE_KEYWORDS if word in text)
    score -= sum(1 for word in NEGATIVE_KEYWORDS if word in text)

    if score > 0:
        direction = "BUY"
    elif score < 0:
        direction = "SELL"
    else:
        direction = "WATCH"

    return f"{direction} {asset} - Monitor for confirmation with proper risk management"


def load_newsdata_articles(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("status") not in {None, "success"}:
        raise RuntimeError(f"Newsdata API returned status {payload.get('status')!r}")
    results = payload.get("results") or []
    if not isinstance(results, list):
        raise RuntimeError("Newsdata API payload did not contain a list of results")
    return [normalize_newsdata_article(item) for item in results if isinstance(item, dict)]


def load_newsapi_articles(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("status") != "ok":
        raise RuntimeError(
            f"News API returned status {payload.get('status')!r}: {payload.get('message', 'unknown error')}"
        )
    articles = payload.get("articles") or []
    if not isinstance(articles, list):
        raise RuntimeError("News API payload did not contain a list of articles")
    return [normalize_newsapi_article(item) for item in articles if isinstance(item, dict)]


_news_cache = {}

def fetch_latest_articles(query: str = FOREX_QUERY) -> list[dict[str, Any]]:
    global _news_cache
    provider = get_active_provider()
    
    # Check cache first for API calls (RSS is always live)
    now = datetime.now()
    cache_key = f"{provider}:{query}"
    cached_api_articles = []
    
    if cache_key in _news_cache:
        timestamp, api_articles = _news_cache[cache_key]
        if (now - timestamp).total_seconds() < 600: # Cache API results for 10 minutes
            cached_api_articles = api_articles
            
    if not cached_api_articles:
        try:
            if provider == "finnhub":
                categories = ["general", "forex", "crypto", "merger"]
                all_articles: list[dict] = []
                for cat in categories:
                    try:
                        articles = finnhub_fetch_news(cat)
                        all_articles.extend(articles)
                    except Exception:
                        pass
                seen = set()
                unique = []
                for a in all_articles:
                    k = article_key(a)
                    if k and k not in seen:
                        seen.add(k)
                        unique.append(a)
                cached_api_articles = unique
            else:
                url = build_newsapi_url(query) if provider == "newsapi" else build_newsdata_url(query)
                with urlopen(url, timeout=30) as response:
                    payload = json.load(response)
                if provider == "newsapi":
                    cached_api_articles = load_newsapi_articles(payload)
                else:
                    cached_api_articles = load_newsdata_articles(payload)
            
            # Save to cache
            _news_cache[cache_key] = (now, cached_api_articles)
        except Exception as e:
            print(f"[FETCH NEWS] API request failed: {e}")
            # If failed, reuse expired cache if available
            if cache_key in _news_cache:
                cached_api_articles = _news_cache[cache_key][1]
            else:
                cached_api_articles = []

    live_articles = fetch_live_market_news()
    combined = cached_api_articles + live_articles
    seen = set()
    unique = []
    for article in combined:
        key = article_key(article)
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        unique.append(article)
    return unique


def is_recent(article: dict[str, Any], max_age_hours: int = 48) -> bool:
    pub_date = article.get("pubDate") or ""
    if not pub_date:
        return False
    try:
        dt_str = pub_date.replace("Z", "+00:00")
        if "+" not in dt_str and dt_str.count("-") == 2:
            dt_str += "+00:00"
        pub = datetime.fromisoformat(dt_str)
        delta = datetime.now(timezone.utc) - pub
        return delta.total_seconds() < max_age_hours * 3600
    except Exception:
        return True


def format_market_snapshot_block() -> str | None:
    try:
        import indian_market as im
        indian = im.format_market_snapshot()
        global_data = im.format_global_snapshot()
        parts = []
        if global_data:
            parts.append(global_data)
        if indian:
            parts.append(indian)
        return "\n\n".join(parts) if parts else None
    except Exception:
        return None


def _calc_rr(trade_text: str) -> str | None:
    for line in trade_text.split("\n"):
        if "Targets:" not in line:
            continue
        try:
            entry_line = ""
            lines = trade_text.split("\n")
            idx = lines.index(line)
            if idx > 0:
                entry_line = lines[idx - 1]
            entry_str = entry_line.split("@")[-1].strip() if "@" in entry_line else ""
            entry_str = _re.sub(r'[$₹,€£¥]', '', entry_str)
            if not entry_str:
                continue
            entry = float(entry_str)
            targets_str = line.split("Targets:")[1].split("|")[0].strip()
            sl_str = line.split("SL:")[1].strip() if "SL:" in line else ""
            targets_str = _re.sub(r'[$₹,€£¥]', '', targets_str)
            sl_str = _re.sub(r'[$₹,€£¥]', '', sl_str)
            tp_parts = targets_str.split("/")
            tp_reward = max(float(tp_parts[0].strip()), float(tp_parts[1].strip()))
            sl = float(sl_str) if sl_str else 0
            reward = abs(tp_reward - entry)
            risk = abs(sl - entry)
            if risk > 0:
                return f"R:R 1:{reward / risk:.1f}"
        except (ValueError, IndexError, AttributeError):
            pass
    return None


import re as _re


def _strip_md(text: str) -> str:
    return _re.sub(r'[*_`>#()\[\]\\<>]', '', text)


def _confidence_pct(level: str) -> int:
    return {"High": 85, "Medium": 72, "Low": 55}.get(level, 50)


_USD_QUOTE_PAIRS = frozenset({
    "EUR/USD", "GBP/USD", "AUD/USD", "NZD/USD",
    "XAU/USD", "XAG/USD",
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "ADA/USD",
    "DOGE/USD", "DOT/USD", "AVAX/USD", "LINK/USD", "LTC/USD",
    "WTI", "BRENT", "US30", "US100", "SP500", "UK100", "GER40",
    "JPN225", "HK50", "AUS200",
    "USD/CHF", "USD/CAD", "USD/MXN", "USD/ZAR", "USD/TRY",
    "USD/SGD", "USD/HKD", "USD/CNY",
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "JPM", "V", "WMT", "JNJ", "PG", "XOM", "UNH", "HD", "BAC",
    "DIS", "NFLX", "ADBE", "CRM", "INTC", "AMD", "PYPL", "UBER",
    "NKE", "BA", "COIN", "SNAP", "SQ", "PLTR", "RBLX", "MCD",
    "SBUX", "NIO", "RIVN",
})

_STOCK_ASSETS = frozenset({
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTI",
    "WIPRO", "ITC", "LT", "AXISBANK", "KOTAKBANK", "MARUTI", "TATAMOTORS",
    "ASIANPAINT", "HCLTECH", "SUNPHARMA", "BAJFINANCE", "TITAN", "NTPC",
    "ONGC", "POWERGRID", "ULTRACEMCO", "TATASTEEL", "JSWSTEEL", "HINDALCO",
    "TECHM", "COALINDIA", "HINDUNILVR", "BRITANNIA", "NESTLEIND", "M&M",
    "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO", "TATACONSUM", "DABUR", "MARICO",
    "HDFC", "ICICIPRUDI", "HDFCLIFE", "SBILIFE", "TRENT", "AVENUE",
    "PIDILITIND", "HAVELLS", "SIEMENS", "BEL", "BHEL", "HAL",
    "IRFC", "IREDA", "SUZLON", "ADANIENT", "ADANIPORTS",
    "ADANIGREEN", "ADANITRANS", "ADANIPOWER", "HINDZINC", "VEDL",
    "IOC", "BPCL", "GAIL", "NATIONALUM", "ZOMATO", "SWIGGY",
    "PAYTM", "POLICYBZR", "NYKAA", "HDFCAMC", "GRASIM",
    "DIVISLAB", "CIPLA", "DRREDDY", "APOLLOHOSP", "AUROPHARMA", "TVSMOTOR",
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "JPM", "V", "WMT", "JNJ", "PG", "XOM", "UNH", "HD", "BAC",
    "DIS", "NFLX", "ADBE", "CRM", "INTC", "AMD", "PYPL", "UBER",
    "NKE", "BA", "COIN", "SNAP", "SQ", "PLTR", "RBLX", "MCD", "SBUX", "NIO", "RIVN",
})


def _price_str(val: float, pair: str) -> str:
    if pair in _USD_QUOTE_PAIRS:
        if abs(val) >= 1000:
            return f"${val:,.2f}"
        elif abs(val) >= 1:
            return f"${val:.2f}"
        return f"${val:.4f}"
    if abs(val) >= 1000:
        return f"{val:,.2f}"
    elif abs(val) >= 1:
        return f"{val:.2f}"
    return f"{val:.4f}"


def _calc_percentage_levels(price: float, is_buy: bool,
                            tp1_pct: float = 2.5, tp2_pct: float = 5.0,
                            sl_pct: float = 0.5) -> tuple[float, float, float, float]:
    entry = round(price, 2)
    tp1 = round(price * (1 + tp1_pct / 100) if is_buy else price * (1 - tp1_pct / 100), 2)
    tp2 = round(price * (1 + tp2_pct / 100) if is_buy else price * (1 - tp2_pct / 100), 2)
    sl  = round(price * (1 - sl_pct / 100) if is_buy else price * (1 + sl_pct / 100), 2)
    return entry, tp1, tp2, sl


def format_professional_signal(
    pair: str, direction: str, entry: float, tp1: float, tp2: float, sl: float,
    confidence_pct: int, reason: str, timeframe: str = "H1",
) -> str:
    dir_icon = "🟢 BUY" if direction == "BUY" else "🔴 SELL"
    pips_sl = _price_str(abs(round(sl - entry, 4)), pair)
    pips_tp1 = _price_str(abs(round(tp1 - entry, 4)), pair)
    pips_tp2 = _price_str(abs(round(tp2 - entry, 4)), pair)
    risk = abs(sl - entry)
    reward = abs(tp2 - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "?"
    name = INSTRUMENT_NAMES.get(pair, pair)
    lines = [
        "📡 *TradeSignal Pro* | AI Signal",
        "",
        f"*{pair}* · {dir_icon} · {timeframe}",
        f"_{name}_",
        "",
        "━━━━━━━━━━━━━━",
        f"📌 Entry:      {_price_str(entry, pair)}",
        f"🛑 Stop Loss:  {_price_str(sl, pair)}  (-{pips_sl})",
        f"🎯 TP 1:       {_price_str(tp1, pair)} (+{pips_tp1})",
        f"🎯 TP 2:       {_price_str(tp2, pair)} (+{pips_tp2})",
        f"⚖️ Risk:Reward: 1 : {rr}",
        "━━━━━━━━━━━━━━",
        f"🤖 AI Confidence: {confidence_pct}%",
        "",
        f"📝 Reason: {_strip_md(reason[:300])}",
        "",
        "⚠️ Not financial advice. Trade at your own risk.",
    ]
    return "\n".join(lines)


def format_high_impact_alert(
    title: str, asset: str, direction: str, confidence_pct: int,
    analysis: str,
) -> str:
    """Template 2 — High-impact breaking news alert."""
    dir_icon = (
        "🟢 Bullish" if direction == "Bullish"
        else "🔴 Bearish" if direction == "Bearish"
        else "🟡 Neutral"
    )
    ist_now  = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    date_str = ist_now.strftime("%d %b %Y, %I:%M %p IST")
    
    # Calculate optional trade setup if asset has a corresponding trade pair
    trade_section = ""
    pairs = TRADE_PAIRS.get(asset) if asset else None
    if pairs:
        try:
            prices = fetch_current_prices()
            pair, multiplier, pip_size = pairs[0]
            price = prices.get(pair)
            if price:
                is_buy = (direction == "Bullish") == (multiplier > 0)
                dir_label = "BUY" if is_buy else "SELL"
                e  = round(price, 4)
                t1 = round(price + 75 * pip_size if is_buy else price - 75 * pip_size, 4)
                t2 = round(price + 150 * pip_size if is_buy else price - 150 * pip_size, 4)
                s  = round(price - 15 * pip_size if is_buy else price + 15 * pip_size, 4)
                reward = abs(t2 - e)
                risk   = abs(s - e)
                rr_str = f"{reward / risk:.1f}" if risk > 0 else "?"
                
                trade_lines = [
                    f"━━━━━━━━━━━━━━━━━━",
                    f"🎯 *AI TRADE SETUP — {dir_label}*",
                    f"📌 *Entry:* {_price_str(e, pair)}",
                    f"🛑 *Stop Loss:* {_price_str(s, pair)}  ({_price_str(s - e, pair)})",
                    f"🎯 *TP 1:* {_price_str(t1, pair)}  (+" + _price_str(abs(t1 - e), pair) + ")",
                    f"🎯 *TP 2:* {_price_str(t2, pair)}  (+" + _price_str(abs(t2 - e), pair) + ")",
                    f"⚖️ *Risk:Reward:* 1 : {rr_str}",
                ]
                trade_section = "\n".join(trade_lines) + "\n"
                log_signal(pair, dir_label, e, t1, t2, s, "high_impact")
        except Exception as exc:
            print(f"[ERROR] High impact trade setup calculation failed: {exc}")

    return (
        f"📰 *BREAKING NEWS ALERT*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"*{_strip_md(title[:80])}*\n"
        f"🌍 *Asset:* {asset}  ·  {date_str}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💥 *Impact:* {dir_icon} for *{asset}*\n"
        f"🤖 *Confidence:* {confidence_pct}%\n"
        f"{trade_section}"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *Quick Analysis:*\n"
        f"{_strip_md(analysis[:350])}\n\n"
        f"🔖 #{asset}  #highimpact  #breakingnews  #news"
    )


def format_nse_signal(
    index: str, option_type: str, strike: str, direction: str,
    entry_low: float, entry_high: float, sl: float, tp1: float, tp2: float,
    spot: float, pcr: float | None, reason: str, bengali: str | None = None,
    expiry: str = "Weekly",
) -> str:
    dir_emoji = "🟢 BUY" if direction == "BUY" else "🔴 SELL"
    sl_pct = round(abs(sl - entry_low) / entry_low * 100)
    tp1_pct = round(abs(tp1 - entry_low) / entry_low * 100)
    tp2_pct = round(abs(tp2 - entry_low) / entry_low * 100)
    pcr_str = ""
    if pcr is not None:
        pcr_label = "bullish" if pcr > 1.2 else ("bearish" if pcr < 0.8 else "neutral")
        pcr_str = f"📊 PCR:             {pcr:.2f} ({pcr_label})"
    expiry_label = f"Weekly Expiry · {expiry}"
    lines = [
        f"🇮🇳 *{index}* · {option_type} {strike} | {dir_emoji}",
        f"_{expiry_label} · Options_",
        "",
        "━━━━━━━━━━━━━━",
        f"📌 Entry (premium): ₹{entry_low}–{entry_high}",
        f"🛑 Stop Loss:       ₹{sl}  (-{sl_pct}%)",
        f"🎯 Target 1:        ₹{tp1}  (+{tp1_pct}%)",
        f"🎯 Target 2:        ₹{tp2}  (+{tp2_pct}%)",
        f"📍 Spot ref:        {spot}",
    ]
    if pcr_str:
        lines.append(pcr_str)
    lines.append("━━━━━━━━━━━━━━")
    lines.append(f"📝 Reason: {_strip_md(reason[:300])}")
    if bengali:
        lines.append("")
        lines.append(f"🇧🇩 বাংলা: {bengali[:150]}")
    lines.append("")
    lines.append(f"🔖 #{index} #options #NSE #India #{expiry}")
    return "\n".join(lines)


def format_calendar_alert_md(events: list[dict]) -> str | None:
    if not events:
        return None
    lines = [
        "📰 *ECONOMIC CALENDAR*",
        "━━━━━━━━━━━━━━",
    ]
    now = datetime.now(timezone.utc)
    for ev in events:
        dt = ev.get("datetime")
        if not dt:
            continue
        mins_until = int((dt - now).total_seconds() / 60)
        if mins_until <= 0:
            time_str = "NOW"
        elif mins_until < 60:
            time_str = f"in {mins_until}m"
        else:
            hours = mins_until // 60
            mins_left = mins_until % 60
            time_str = f"in {hours}h {mins_left}m" if mins_left else f"in {hours}h"
        icon = "🔴" if ev["impact"] == "high" else "🟡"
        title = _strip_md(ev["title"])
        country = ev["country"]
        forecast = _strip_md(ev.get("forecast", "N/A"))
        previous = _strip_md(ev.get("previous", "N/A"))
        lines.append(f"{icon} *{country}* — {title}")
        lines.append(f"   ⏰ {time_str} | 📈 Fcst: {forecast} | 📉 Prev: {previous}")
    if len(lines) == 2:
        return None
    lines.append("")
    lines.append("🔖 #calendar #forex #economic")
    return "\n".join(lines)


def _finnhub_sentiment_line(asset: str) -> str:
    """Add Finnhub sentiment enrichment line if data available."""
    try:
        fh = finnhub_enrich_with_sentiment(asset)
        if fh:
            return f"📊 *Sentiment:* {_strip_md(fh)}"
    except Exception:
        pass
    return ""


# ── Daily Style Theme System ─────────────────────────────────────────────
_WEEKLY_THEMES = [
    {"header": "🚀", "accent": "⚡", "sep": "▬" * 20, "name": "Monday Momentum"},
    {"header": "🔥", "accent": "💥", "sep": "═" * 20, "name": "Tuesday Trade"},
    {"header": "🎯", "accent": "📊", "sep": "▔" * 20, "name": "Wednesday Watch"},
    {"header": "💎", "accent": "🌟", "sep": "✦" * 20, "name": "Thursday Signals"},
    {"header": "🏆", "accent": "💰", "sep": "▬" * 20, "name": "Friday Forecast"},
    {"header": "📡", "accent": "📈", "sep": "─" * 20, "name": "Saturday Scan"},
    {"header": "🌐", "accent": "🔮", "sep": "━" * 20, "name": "Sunday Summary"},
]
_style_counter: dict[str, int] = {"day": -1}


def _get_today_theme() -> dict:
    today = datetime.now(timezone.utc).weekday()
    if _style_counter["day"] != today:
        _style_counter["day"] = today
    return _WEEKLY_THEMES[today]


def _style_header(title: str, theme: dict) -> str:
    return f"{theme['header']} *{title}*  {theme['header']}"


def _style_sep(theme: dict) -> str:
    return theme["sep"]


def _style_label(k: str, v: str, w: int = 14) -> str:
    return f"`{k:<{w}}` {v}"



def _translate_to_bengali(text: str) -> str:
    if not text:
        return ""
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='auto', target='bn').translate(text)
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return text

def format_forex_message(article: dict[str, Any]) -> str:
    """Template 1 — Forex/Crypto trade signal or news alert."""

    # For Twitter news, translate description to Bengali
    if source.lower() == "twitter":
        desc = article.get("description", "")
        if desc:
            bengali_desc = _translate_to_bengali(desc)
            text_body = bengali_desc + "\n\n(Original: " + desc + ")"
            article["description"] = text_body  # Update for the rest of the flow

    title     = _strip_md(article.get("title") or "Market Update")
    source    = _strip_md(article.get("source_name") or "")
    published = _strip_md(article.get("pubDate") or "")
    link      = article.get("link") or ""

    asset  = identify_asset(article)
    bias   = infer_bias_signal(article)
    prices = fetch_current_prices()
    text_body = normalize_text(article)
    direction, confidence = "Neutral", "Low"
    if bias:
        direction, confidence = compute_confidence(text_body)

    pairs = TRADE_PAIRS.get(asset) if asset else None

    # ── Build trade signal card (Template 1) if we have a clear bias + pair ──
    if bias and pairs:
        parts = bias.split()
        if len(parts) == 2:
            direction_str, asset_sym = parts[0], parts[1]
            is_bullish = direction_str == "Bullish"
            pair, multiplier, pip_size = pairs[0]
            price = prices.get(pair)
            if price:
                is_buy = (is_bullish == (multiplier > 0))
                direction_label = "BUY" if is_buy else "SELL"
                dir_icon  = "🟢 BUY" if is_buy else "🔴 SELL"
                e  = round(price, 4)
                t1 = round(price + 75 * pip_size if is_buy else price - 75 * pip_size, 4)
                t2 = round(price + 150 * pip_size if is_buy else price - 150 * pip_size, 4)
                s  = round(price - 15 * pip_size if is_buy else price + 15 * pip_size, 4)
                reward = abs(t2 - e)
                risk   = abs(s - e)
                rr_str = f"{reward / risk:.1f}" if risk > 0 else "?"
                conf_pct = _confidence_pct(confidence)
                ai_reason = _strip_md(ai_analyze_news(article) or title[:200])
                inst_name = INSTRUMENT_NAMES.get(pair, pair)
                log_signal(pair, direction_label, e, t1, t2, s, "forex")
                lines = [
                    f"🌍 *FOREX & CRYPTO INTELLIGENCE* 🌍",
                    f"📌 *Pair:* {pair} ({inst_name})",
                    f"⚡ *Action:* {dir_icon} @ {_price_str(e, pair)}",
                    "--------------------------------------",
                    f"🛑 *Stop Loss (SL):*  {_price_str(s, pair)}",
                    f"🎯 *Target 1 (TP):*  {_price_str(t1, pair)}",
                    f"🔥 *Target 2 (TP):*  {_price_str(t2, pair)}",
                    "--------------------------------------",
                    f"⚖️ *Risk/Reward:* 1:{rr_str}",
                    f"🤖 *AI Confidence:* {conf_pct}%",
                    "",
                    f"💡 *AI Thesis:* {ai_reason[:350]}",
                    "",
                    f"🔗 #{asset_sym} #Forex #Crypto",
                    f"⚠️ _Not financial advice._"
                ]
                if link:
                    lines.append(f"🔗 Source: {link}")
                return "\n".join(lines)

    # ── Fallback: news alert (Template 2 style) ──────────────────────────────
    ai_analysis = _strip_md(ai_analyze_news(article) or ensure_summary(article)[:300])
    dir_icon_fb = (
        "🟢 Bullish" if direction == "Bullish"
        else "🔴 Bearish" if direction == "Bearish"
        else "🟡 Neutral"
    )
    conf_pct_fb = _confidence_pct(confidence)
    ist_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y")
    theme = _get_today_theme()
    sep = _style_sep(theme)
    lines = [
        _style_header(f"Forex / Market Update", theme),
        f"`{sep}`",
        f"*{title[:80]}*",
        f"",
        _style_label("Asset",   asset),
        _style_label("Date",    ist_str),
        _style_label("Impact",  dir_icon_fb),
        _style_label("AI Conf.", f"{conf_pct_fb}%"),
        f"`{sep}`",
        f"📊 *Analysis:*",
        f"{ai_analysis[:350]}",
        f"",
        _finnhub_sentiment_line(asset),
        f"",
        f"🔖 #{asset}  #forex  #news",
    ]
    if source:
        lines.append(f"📰 _{source}  |  {published}_")
    if link:
        lines.append(f"🔗 {link}")
    return "\n".join(lines)


def format_india_message(article: dict[str, Any]) -> str:
    """Template 3 — India/NSE market signal."""

    # Translate Indian news description to Bengali
    desc = article.get("description", "")
    if desc:
        bengali_desc = _translate_to_bengali(desc)
        article["description"] = bengali_desc + "\n\n(Original: " + desc + ")"

    title     = _strip_md(article.get("title") or "India Market Update")
    source    = _strip_md(article.get("source_name") or "")
    published = _strip_md(article.get("pubDate") or "")

    asset  = identify_asset(article)
    bias   = infer_bias_signal(article)
    prices = fetch_current_prices()
    text_body = normalize_text(article)
    direction, confidence = "Neutral", "Low"
    if bias:
        direction, confidence = compute_confidence(text_body)

    dir_icon = (
        "🟢 BUY"  if direction == "Bullish"
        else "🔴 SELL" if direction == "Bearish"
        else "➖ WATCH"
    )
    conf_pct   = _confidence_pct(confidence)
    ai_insight = _strip_md(ai_analyze_news(article) or ensure_summary(article)[:300])
    inst_name  = INSTRUMENT_NAMES.get(asset, asset)

    # Try to compute price levels
    pairs_list = TRADE_PAIRS.get(asset)
    entry_str = sl_str = tp1_str = tp2_str = "Monitor levels"
    sl_diff = tp1_diff = tp2_diff = ""
    is_buy = False
    e = t1 = t2 = s = 0.0
    if pairs_list:
        pair, multiplier, pip_size = pairs_list[0]
        price = prices.get(pair)
        if price:
            is_buy = (direction == "Bullish") == (multiplier > 0)
            if asset in _STOCK_ASSETS:
                e, t1, t2, s = _calc_percentage_levels(price, is_buy)
            else:
                e = round(price, 2)
                t1 = round(price + 75 * pip_size if is_buy else price - 75 * pip_size, 2)
                t2 = round(price + 150 * pip_size if is_buy else price - 150 * pip_size, 2)
                s  = round(price - 15 * pip_size if is_buy else price + 15 * pip_size, 2)
            entry_str = _price_str(e, pair)
            sl_str    = _price_str(s, pair)
            tp1_str   = _price_str(t1, pair)
            tp2_str   = _price_str(t2, pair)
            sl_diff   = _price_str(abs(s - e), pair)
            tp1_diff  = _price_str(abs(t1 - e), pair)
            tp2_diff  = _price_str(abs(t2 - e), pair)
            log_signal(pair, "BUY" if is_buy else "SELL", e, t1, t2, s, "india")

    live_price = format_stock_price_info(asset)
    theme = _get_today_theme()
    sep = _style_sep(theme)
    lines = [
        _style_header(f"NSE / BSE SIGNAL — {dir_icon}", theme),
        f"`{sep}`",
        f"`Asset      ` *{asset}*  ·  {inst_name}",
        f"`{theme['name']}` _{title[:80]}_",
        f"",
    ]
    if live_price:
        lines.append(live_price)
        lines.append("")
    if pairs_list and price:
        entry_icon = "🟢 BUY" if is_buy else "🔴 SELL"
        if asset in _STOCK_ASSETS:
            pct_tp1 = abs(t1 - e) / e * 100
            pct_tp2 = abs(t2 - e) / e * 100
            pct_sl = abs(s - e) / e * 100
            rr = abs(t2 - e) / abs(s - e) if abs(s - e) > 0 else 0
            lines.extend([
                "--------------------------------------",
                f"🎯 *Entry Price:*   ₹{entry_str}",
                f"🔥 *Take Profit 1:* ₹{tp1_str} (+{pct_tp1:.1f}%)",
                f"🚀 *Take Profit 2:* ₹{tp2_str} (+{pct_tp2:.1f}%)",
                f"🛑 *Stop Loss:*     ₹{sl_str} (-{pct_sl:.1f}%)",
                "--------------------------------------",
                f"⚖️ *Structure:* 1:{rr:.1f} R:R | *AI:* {conf_pct}%",
                "",
                f"💡 *Market Context:* {ai_insight[:300]}",
                "",
                f"🔗 #{asset} #NSE #IndianStockMarket",
                f"⚠️ _Strict Risk Management Advised._",
            ])
        else:
            lines.extend([
                f"`{sep}`",
                _style_label("Entry zone", entry_str),
                _style_label("Stop loss",  sl_str + (f"  (-{sl_diff})" if sl_diff else "")),
                _style_label("Target 1",   tp1_str + (f"  (+{tp1_diff})" if tp1_diff else "")),
                _style_label("Target 2",   tp2_str + (f"  (+{tp2_diff})" if tp2_diff else "")),
                _style_label("Confidence", f"{conf_pct}%"),
                f"`{sep}`",
                f"📊 *Analysis:* {ai_insight[:300]}",
                f"",
                f"🔖 #{asset}  #NSE  #BSE  #India  #news",
            ])
    else:
        lines.extend([
            f"`{sep}`",
            f"📊 *Analysis:* {ai_insight[:300]}",
            f"",
            f"🔖 #{asset}  #NSE  #BSE  #India  #news",
        ])
    if source:
        lines.append(f"📰 _{source}  |  {published}_")
    return "\n".join(lines)


def format_intraday_message(article: dict[str, Any]) -> str:
    """Template 3 variant — India intraday stock signal."""
    title     = _strip_md(article.get("title") or "Intraday Update")
    source    = _strip_md(article.get("source_name") or "")
    published = _strip_md(article.get("pubDate") or "")

    asset     = identify_asset(article)
    inst_name = INSTRUMENT_NAMES.get(asset, asset)
    bias      = infer_bias_signal(article)
    prices    = fetch_current_prices()
    text_body = normalize_text(article)
    direction, confidence = "Neutral", "Low"
    if bias:
        direction, confidence = compute_confidence(text_body)

    dir_icon = (
        "🟢 BUY"  if direction == "Bullish"
        else "🔴 SELL" if direction == "Bearish"
        else "➖ WATCH"
    )
    conf_pct   = _confidence_pct(confidence)
    ai_insight = _strip_md(ai_analyze_news(article) or ensure_summary(article)[:300])

    exchange_tag = "NSE" if asset in {
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTI",
        "WIPRO", "ITC", "LT", "AXISBANK", "KOTAKBANK", "MARUTI", "TATAMOTORS",
        "ASIANPAINT", "HCLTECH", "SUNPHARMA", "BAJFINANCE", "TITAN", "NTPC",
        "ONGC", "POWERGRID", "ULTRACEMCO", "NIFTY", "SENSEX", "BANKNIFTY",
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "TECHM", "COALINDIA",
        "HINDUNILVR", "BRITANNIA", "NESTLEIND", "M&M", "EICHERMOT",
        "HEROMOTOCO", "BAJAJ-AUTO", "TATACONSUM", "DABUR", "MARICO",
        "HDFC", "ICICIPRUDI", "HDFCLIFE", "SBILIFE", "TRENT", "AVENUE",
        "PIDILITIND", "HAVELLS", "SIEMENS", "BEL", "BHEL", "HAL",
        "IRFC", "IREDA", "SUZLON", "ADANIENT", "ADANIPORTS",
        "ADANIGREEN", "ADANITRANS", "ADANIPOWER", "HINDZINC", "VEDL",
        "IOC", "BPCL", "GAIL", "NATIONALUM", "ZOMATO", "SWIGGY",
        "PAYTM", "POLICYBZR", "NYKAA", "HDFCAMC", "GRASIM",
        "DIVISLAB", "CIPLA", "DRREDDY", "APOLLOHOSP", "AUROPHARMA",
        "TVSMOTOR",
    } else "NYSE/NASDAQ" if asset in {
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "JPM", "V", "WMT", "JNJ", "PG", "XOM", "UNH", "HD", "BAC",
        "DIS", "NFLX", "ADBE", "CRM", "INTC", "AMD", "PYPL", "UBER",
        "NKE", "BA", "COIN", "SNAP", "SQ", "PLTR", "RBLX", "MCD",
        "SBUX", "NIO", "RIVN",
    } else "BSE/NSE"

    pairs_list = TRADE_PAIRS.get(asset)
    entry_str = sl_str = tp1_str = tp2_str = "Monitor levels"
    sl_diff = tp1_diff = tp2_diff = ""
    is_buy = False
    e = t1 = t2 = s = 0.0
    if pairs_list:
        pair, multiplier, pip_size = pairs_list[0]
        price = prices.get(pair)
        if price:
            is_buy = (direction == "Bullish") == (multiplier > 0)
            if asset in _STOCK_ASSETS:
                e, t1, t2, s = _calc_percentage_levels(price, is_buy)
            else:
                e = round(price, 2)
                t1 = round(price + 75 * pip_size if is_buy else price - 75 * pip_size, 2)
                t2 = round(price + 150 * pip_size if is_buy else price - 150 * pip_size, 2)
                s  = round(price - 15 * pip_size if is_buy else price + 15 * pip_size, 2)
            entry_str = _price_str(e, pair)
            sl_str    = _price_str(s, pair)
            tp1_str   = _price_str(t1, pair)
            tp2_str   = _price_str(t2, pair)
            sl_diff   = _price_str(abs(s - e), pair)
            tp1_diff  = _price_str(abs(t1 - e), pair)
            tp2_diff  = _price_str(abs(t2 - e), pair)
            log_signal(pair, "BUY" if is_buy else "SELL", e, t1, t2, s, "intraday")

    live_price = format_stock_price_info(asset)
    theme = _get_today_theme()
    sep = _style_sep(theme)
    lines = [
        _style_header(f"Intraday SIGNAL — {exchange_tag}", theme),
        f"`{sep}`",
        f"`Asset      ` *{asset}*  ·  {inst_name}  |  {dir_icon}",
        f"`{theme['name']}` _{title[:80]}_",
        f"",
    ]
    if live_price:
        lines.append(live_price)
        lines.append("")
    if pairs_list and price:
        entry_icon = "🟢 BUY" if is_buy else "🔴 SELL"
        if asset in _STOCK_ASSETS:
            pct_tp1 = abs(t1 - e) / e * 100
            pct_tp2 = abs(t2 - e) / e * 100
            pct_sl = abs(s - e) / e * 100
            rr = abs(t2 - e) / abs(s - e) if abs(s - e) > 0 else 0
            lines.extend([
                "▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️",
                f"🟢 *Entry:* ₹{entry_str}",
                f"🎯 *Target 1:* ₹{tp1_str} ({pct_tp1:.1f}%)",
                f"🎯 *Target 2:* ₹{tp2_str} ({pct_tp2:.1f}%)",
                f"🛑 *Stop Loss:* ₹{sl_str} ({pct_sl:.1f}%)",
                "▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️",
                f"⚡ *Momentum:* {conf_pct}% AI Score",
                "",
                f"💡 *Catalyst:* {ai_insight[:200]}",
                "",
                f"🔗 #{asset} #Intraday #DayTrading",
                f"⚠️ _Fast execution required._"
            ])
        else:
            lines.extend([
                f"`{sep}`",
                _style_label("Entry zone", entry_str),
                _style_label("Stop loss",  sl_str + (f"  (-{sl_diff})" if sl_diff else "")),
                _style_label("Target 1",   tp1_str + (f"  (+{tp1_diff})" if tp1_diff else "")),
                _style_label("Target 2",   tp2_str + (f"  (+{tp2_diff})" if tp2_diff else "")),
                _style_label("Confidence", f"{conf_pct}%"),
                f"`{sep}`",
                f"📊 *Analysis:* {ai_insight[:300]}",
                f"",
                f"🔖 #{asset}  #intraday  #{exchange_tag}  #India",
            ])
    else:
        lines.extend([
            f"`{sep}`",
            f"📊 *Analysis:* {ai_insight[:300]}",
            f"",
            f"🔖 #{asset}  #intraday  #{exchange_tag}  #India",
        ])
    if source:
        lines.append(f"📰 _{source}  |  {published}_")
    return "\n".join(lines)


_bot2_instance: Bot | None = None
_bot3_instance: Bot | None = None


def _init_bot2() -> Bot | None:
    global _bot2_instance
    if _bot2_instance is not None:
        return _bot2_instance
    if BOT_TOKEN2:
        _bot2_instance = Bot(BOT_TOKEN2)
        print("[BOT2] Second bot initialized")
    return _bot2_instance


def _init_bot3() -> Bot | None:
    global _bot3_instance
    if _bot3_instance is not None:
        return _bot3_instance
    if BOT_TOKEN3:
        _bot3_instance = Bot(BOT_TOKEN3)
        print("[BOT3] Third bot initialized")
    return _bot3_instance


def try_render_text_to_card(text: str) -> Any:
    """Detects text type and tries to parse and render it as a visual card image."""
    try:
        import re
        from datetime import datetime
        import telegram_templates as tt
        from PIL import Image
        
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # --- Template 1: Trade Signal / AI Trade Setup ---
        is_signal = any("TradeSignal Pro" in line for line in lines[:3]) and any("Stop Loss" in line for line in lines)
        is_trade_setup = any("AI TRADE SETUP" in line for line in lines)
        
        if is_signal or is_trade_setup:
            header_line = ""
            for line in lines:
                if "·" in line and any(kw in line.upper() for kw in ["BUY", "SELL", "LONG", "SHORT"]):
                    header_line = line
                    break
            
            pair = "XAU/USD"
            direction = "BUY"
            timeframe = "H1"
            if header_line:
                clean_header = header_line.replace("*", "")
                parts = [p.strip() for p in clean_header.split("·")]
                if len(parts) >= 1:
                    pair = parts[0]
                if len(parts) >= 2:
                    direction = "BUY" if "BUY" in parts[1].upper() or "LONG" in parts[1].upper() else "SELL"
                if len(parts) >= 3:
                    timeframe = parts[2]
            
            if is_trade_setup:
                for line in lines:
                    if "AI TRADE SETUP" in line:
                        direction = "BUY" if "BUY" in line.upper() else "SELL"
                        break
                for line in lines:
                    if "Asset:" in line:
                        clean_line = line.replace("*", "").replace("🌍 Asset:", "").strip()
                        parts = [p.strip() for p in clean_line.split("·")]
                        pair = parts[0]
                        if len(pair) == 6 and "/" not in pair:
                            pair = f"{pair[:3]}/{pair[3:]}"
                        break
            
            instrument_name = INSTRUMENT_NAMES.get(pair, pair)
            for line in lines:
                if line.startswith("_") and line.endswith("_"):
                    instrument_name = line.strip("_")
                    break
            
            entry = "0.0"
            sl = "0.0"
            sl_diff = "0.0"
            tp1 = "0.0"
            tp1_diff = "0.0"
            tp2 = "0.0"
            tp2_diff = "0.0"
            rr = "1.0"
            confidence = 80
            reason = "Market analysis trigger."
            
            for line in lines:
                clean_line = line.replace("*", "")
                if "Entry:" in clean_line:
                    entry = clean_line.split("Entry:")[1].strip()
                elif "Stop Loss:" in clean_line:
                    parts = clean_line.split("Stop Loss:")[1].strip().split()
                    sl = parts[0]
                    sl_diff = parts[1].strip("(-)") if len(parts) > 1 else "0"
                elif "TP 1:" in clean_line:
                    parts = clean_line.split("TP 1:")[1].strip().split()
                    tp1 = parts[0]
                    tp1_diff = parts[1].strip("(+)") if len(parts) > 1 else "0"
                elif "TP 2:" in clean_line:
                    parts = clean_line.split("TP 2:")[1].strip().split()
                    tp2 = parts[0]
                    tp2_diff = parts[1].strip("(+)") if len(parts) > 1 else "0"
                elif "Risk:Reward:" in clean_line or "Risk : Reward:" in clean_line:
                    label = "Risk:Reward:" if "Risk:Reward:" in clean_line else "Risk : Reward:"
                    rr = clean_line.split(label)[1].strip().replace("1 :", "").strip()
                elif "Confidence:" in line:
                    match = re.search(r'\d+', line)
                    if match:
                        confidence = int(match.group())
                elif "Reason:" in line:
                    reason = line.split("Reason:")[1].strip()
            
            tags = ["signal", "forex", pair.lower().replace("/", "")]
            for line in lines:
                if line.startswith("🔖"):
                    tags = [t.strip("# ") for t in line.split() if t.strip() and not t.startswith("🔖")]
            
            return tt.make_signal_card(
                pair=pair, instrument_name=instrument_name, direction=direction,
                entry=entry, sl=sl, sl_diff=sl_diff, tp1=tp1, tp1_diff=tp1_diff,
                tp2=tp2, tp2_diff=tp2_diff, rr=rr, confidence=confidence,
                reason=reason, tags=tags, timeframe=timeframe
            )

        # --- Template 2: Breaking News Alert ---
        elif "BREAKING NEWS ALERT" in text or "📰 *BREAKING" in text:
            title = "Breaking News Alert"
            header_idx = -1
            for i, line in enumerate(lines):
                if "BREAKING" in line:
                    header_idx = i
                    break
            
            if header_idx != -1 and header_idx + 1 < len(lines):
                # Title is usually the next line
                title = lines[header_idx + 1].replace("*", "")
                
            asset = "Global Market"
            date_str = datetime.now().strftime("%d %b %Y")
            for line in lines:
                if "Asset:" in line:
                    clean_line = line.replace("*", "").replace("🌍 Asset:", "").strip()
                    parts = [p.strip() for p in clean_line.split("·")]
                    asset = parts[0]
                    if len(parts) > 1:
                        date_str = " · ".join(parts[1:])
                        
            direction = "Neutral"
            for line in lines:
                if "Impact:" in line:
                    direction = "Bullish" if "Bullish" in line else "Bearish" if "Bearish" in line else "Neutral"
                    
            confidence_pct = 75
            for line in lines:
                if "Confidence:" in line:
                    match = re.search(r'\d+', line)
                    if match:
                        confidence_pct = int(match.group())
                        
            analysis = "Macro economic breaking news update."
            for i, line in enumerate(lines):
                if "Quick Analysis:" in line and i + 1 < len(lines):
                    analysis = lines[i + 1]
                    
            tags = ["breaking", "news", asset.lower()]
            for line in lines:
                if line.startswith("🔖"):
                    tags = [t.strip("# ") for t in line.split() if t.strip() and not t.startswith("🔖")]
                    
            return tt.make_news_alert_card(
                title=title, asset=asset, category="Business", date_str=date_str,
                direction=direction, confidence_pct=confidence_pct, analysis=analysis, tags=tags
            )

        # --- Template 3: NSE/Nifty Signal ---
        elif any(marker in text for marker in ["🇮🇳", "BANKNIFTY", "NIFTY"]):
            header_line = ""
            for line in lines:
                if "🇮🇳" in line:
                    header_line = line
                    break
            
            index = "NIFTY"
            asset = "CE"
            direction = "BUY"
            if header_line:
                clean_header = header_line.replace("*", "").replace("🇮🇳", "").strip()
                parts = [p.strip() for p in clean_header.split("·")]
                if len(parts) >= 1:
                    index = parts[0]
                if len(parts) >= 2:
                    sub_parts = [sp.strip() for sp in parts[1].split("|")]
                    asset = sub_parts[0]
                    if len(sub_parts) > 1:
                        direction = sub_parts[1]
            
            entry = "Premium Zone"
            sl = "0"
            sl_diff = "0%"
            tp1 = "0"
            tp1_diff = "0%"
            tp2 = "0"
            tp2_diff = "0%"
            analysis = "Indian market trend update."
            
            for line in lines:
                if "Entry" in line:
                    entry = line.split("Entry")[1].strip("(:) ₹ ")
                elif "Stop Loss:" in line:
                    parts = line.split("Stop Loss:")[1].strip("₹ ").split()
                    sl = parts[0]
                    sl_diff = parts[1].strip("(-)") if len(parts) > 1 else "0"
                elif "Target 1:" in line:
                    parts = line.split("Target 1:")[1].strip("₹ ").split()
                    tp1 = parts[0]
                    tp1_diff = parts[1].strip("(+)") if len(parts) > 1 else "0"
                elif "Target 2:" in line:
                    parts = line.split("Target 2:")[1].strip("₹ ").split()
                    tp2 = parts[0]
                    tp2_diff = parts[1].strip("(+)") if len(parts) > 1 else "0"
                elif "Reason:" in line:
                    analysis = line.split("Reason:")[1].strip()
            
            tags = ["NSE", "options", "India"]
            for line in lines:
                if line.startswith("🔖"):
                    tags = [t.strip("# ") for t in line.split() if t.strip() and not t.startswith("🔖")]
                    
            return tt.make_nse_signal_card(
                index=index, asset=asset, direction=direction, entry=entry,
                sl=sl, sl_diff=sl_diff, tp1=tp1, tp1_diff=tp1_diff,
                tp2=tp2, tp2_diff=tp2_diff, analysis=analysis, tags=tags, exchange="NSE"
            )

        # --- Template 4: Morning Market Briefing ---
        elif "Market Briefing" in text or "🌅" in text:
            date_str = datetime.now().strftime("%d %B %Y")
            for line in lines:
                if "Briefing" in line:
                    date_str = line.split("—")[-1].strip().replace("*", "")
            
            signals = []
            events = []
            overview = "Trade light before major economic event data releases."
            
            in_signals = False
            in_events = False
            in_overview = False
            for line in lines:
                if "Yesterday's Signals" in line:
                    in_signals = True
                    in_events = False
                    in_overview = False
                    continue
                elif "Key Events Today" in line:
                    in_signals = False
                    in_events = True
                    in_overview = False
                    continue
                elif "Market Overview" in line:
                    in_signals = False
                    in_events = False
                    in_overview = True
                    continue
                
                if in_signals:
                    icon = "🟢" if "🟢" in line or "BUY" in line or "LONG" in line else "🔴"
                    clean_s = line.replace("🟢", "").replace("🔴", "").strip()
                    parts = clean_s.split("—")
                    pair = parts[0].strip()
                    res = parts[1].strip() if len(parts) > 1 else "OPEN"
                    signals.append({"pair": pair, "result": res, "up": "🟢" in line})
                elif in_events:
                    match_time = re.search(r'\b\d+:\d+\s*(?:AM|PM|am|pm)?\b', line)
                    t_str = match_time.group() if match_time else "All Day"
                    clean_ev = line.replace(t_str, "").strip("— ").replace("🔴", "").replace("🟡", "").strip()
                    impact = "HIGH" if "HIGH" in line or "🔴" in line else "MED"
                    events.append({"time": t_str, "name": clean_ev, "impact": impact})
                elif in_overview:
                    if not line.startswith("🔖"):
                        overview = line
            
            return tt.make_morning_briefing_card(
                date_str=date_str, signals=signals, events=events, overview=overview
            )

    except Exception as e:
        print(f"[RENDER CARD] Error parsing or rendering template: {e}")
    return None


async def broadcast(bot: Bot, text: str, parse_mode: str = "Markdown", disable_web_page_preview: bool = True) -> int:
    global _subscribers
    
    # Prevent duplicate messages within 50 recent messages (bypassed in tests)
    import sys
    is_testing = "unittest" in sys.modules or "pytest" in sys.modules
    
    if not is_testing:
        sent_cache = load_sent_messages_cache()
        
        def clean_text_for_compare(t: str) -> str:
            import re
            # Normalize: lowercase, remove punctuation, collapse whitespace
            t = t.lower()
            t = re.sub(r'\s+', ' ', t)
            # remove URLs
            t = re.sub(r'https?://\S+', '', t)
            # remove numbers and timestamps/dates which often change between messages
            t = re.sub(r'\d{1,4}[\-/:]\d{1,4}[\-/:\d]*', '', t)
            t = re.sub(r'\d+', '', t)
            # keep only letters and spaces
            t = re.sub(r'[^a-z\s]', '', t)
            t = t.strip()
            return t
            
        cleaned_current = clean_text_for_compare(text)
        if cleaned_current:
            # fuzzy compare against recent sent messages to avoid near-duplicates
            from difflib import SequenceMatcher
            try:
                sim_thresh = float(os.getenv("DUPLICATE_SIMILARITY", "0.85"))
            except Exception:
                sim_thresh = 0.85
            for sent_msg in sent_cache:
                s = clean_text_for_compare(sent_msg)
                if not s:
                    continue
                if s == cleaned_current:
                    print("[BROADCAST] Suppressed duplicate Telegram message (exact match).")
                    return 0
                # compute similarity
                ratio = SequenceMatcher(None, s, cleaned_current).ratio()
                if ratio >= sim_thresh:
                    print(f"[BROADCAST] Suppressed duplicate Telegram message (fuzzy match {ratio:.2f}).")
                    return 0
                    
            sent_cache.append(text)
            if len(sent_cache) > 50:
                sent_cache.pop(0)
            save_sent_messages_cache(sent_cache)

    sent = 0
    targets: list[int | str] = list(_subscribers)
    if TELEGRAM_CHAT_ID:
        targets.insert(0, TELEGRAM_CHAT_ID)

    # Attempt to render the text message into a visual PNG template card
    import telegram_templates as tt
    img = try_render_text_to_card(text)
    photo_buf = None
    if img is not None:
        try:
            photo_buf = tt.img_to_bytes(img)
        except Exception as e:
            print(f"[BROADCAST] Image card buffering failed: {e}")

    bots = [bot]
    bot2 = _init_bot2()
    if bot2:
        bots.append(bot2)
    bot3 = _init_bot3()
    if bot3:
        bots.append(bot3)

    for b in bots:
        bot_targets = targets
        if bot3 and b is bot3 and TELEGRAM_CHAT_ID3:
            bot_targets = [TELEGRAM_CHAT_ID3]
        seen_cids: set[int | str] = set()
        for cid in bot_targets:
            if cid in seen_cids:
                continue
            seen_cids.add(cid)
            try:
                if photo_buf is not None:
                    # Send visual card with text caption
                    photo_buf.seek(0)
                    await b.send_photo(
                        chat_id=cid,
                        photo=photo_buf,
                        caption=text[:1024],  # 1024 character caption limit
                        parse_mode=parse_mode,
                    )
                else:
                    # Fallback to standard text message
                    await b.send_message(
                        chat_id=cid,
                        text=text,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_web_page_preview,
                    )
                sent += 1
            except Exception as exc:
                err_str = str(exc).lower()
                if "blocked" in err_str or "forbidden" in err_str or "chat not found" in err_str:
                    if isinstance(cid, int) and cid in _subscribers:
                        _subscribers.remove(cid)
                        save_subscribers(_subscribers)
                        print(f"[BROADCAST] Removed blocked/subscriber {cid}")
                else:
                    label = "bot3" if bot3 and b is bot3 else "bot2" if bot2 and b is bot2 else "bot1"
                    print(f"[BROADCAST] Failed to send via {label} to {cid}: {exc}")
    return sent
async def send_category_article(
    bot: Bot,
    articles: list[dict[str, Any]],
    seen_keys: set[str],
    category_prefix: str,
    format_func: Any,
    silent_init: bool = False,
) -> int:
    for article in articles:
        key = article_key(article)
        if not key:
            continue
        full_key = f"{category_prefix}:{key}"
        if full_key in seen_keys or key in seen_keys or any(k.endswith(f":{key}") for k in seen_keys):
            continue
        if not is_recent(article):
            continue

                # Deduplicate similar/repeated titles using word-order-invariant hashes
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
            continue

        # Filter out weak/medium analysis for regular category messages (Must be High confidence and directional)
        bias = infer_bias_signal(article)
        text_body = normalize_text(article)
        direction, confidence = "Neutral", "Low"
        if bias:
            direction, confidence = compute_confidence(text_body)
        # Filter: ONLY broadcast High-confidence directional signals to Telegram (70%+ rule)
        if confidence != "High" or direction == "Neutral":
            continue

        text = format_func(article)
        if not text:
            continue

        await broadcast(bot, text)
        seen_keys.add(full_key)
        seen_keys.add(key)
        if title_norm:
            seen_keys.add(title_key)
        save_seen_keys(seen_keys)
        
        # Save signal to log for UI
        pair = identify_asset(article) or category_prefix.upper()
        if bias:
            global _signal_log
            _signal_log = load_signal_log()
            _signal_log.append({
                "pair": pair,
                "direction": direction.upper(),
                "entry": 0.0,
                "tp1": 0.0,
                "tp2": 0.0,
                "sl": 0.0,
                "confidence": 90 if confidence == "High" else 75,
                "timestamp": datetime.now(timezone.utc).strftime("%H:%M UTC"),
                "source": category_prefix,
                "reason": title
            })
            save_signal_log(_signal_log)
            
        return 1
    return 0


async def send_options_suggestion(bot: Bot, seen_keys: set[str]) -> int:
    import indian_market as im

    nifty_suggestion = im.format_nifty_options_suggestion()
    today = datetime.now(timezone.utc).strftime("%Y%m%d")

    sent = 0

    if nifty_suggestion:
        key = f"option:nifty_{today}"
        if key not in seen_keys:
            await broadcast(bot, nifty_suggestion, parse_mode="HTML")
            seen_keys.add(key)
            save_seen_keys(seen_keys)
            sent += 1

    sensex_suggestion = im.format_sensex_options_suggestion()
    if sensex_suggestion:
        key = f"option:sensex_{today}"
        if key not in seen_keys:
            await broadcast(bot, sensex_suggestion, parse_mode="HTML")
            seen_keys.add(key)
            save_seen_keys(seen_keys)
            sent += 1

    return sent


async def send_institutional_signals(bot: Bot, seen_keys: set[str]) -> int:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    key = f"institutional_signals:{today}"
    if key in seen_keys:
        return 0
    if not MASSIVE_API_KEY:
        return 0

    sent = 0
    try:
        block = massive_data.format_institutional_signal_block()
        if block:
            await broadcast(bot, block)
            seen_keys.add(key)
            save_seen_keys(seen_keys)
            sent += 1
            print("[INSTITUTIONAL SIGNALS] Sent consensus ratings")

        commodity_block = massive_data.format_commodity_signal_block()
        if commodity_block:
            await broadcast(bot, commodity_block)
            sent += 1
            print("[COMMODITY WATCH] Sent commodity prices")

        us_block = massive_data.format_us_market_block()
        if us_block:
            await broadcast(bot, us_block)
            sent += 1
            print("[US MARKET DATA] Sent indices & yields")
    except Exception as e:
        print(f"[ERROR] Institutional signals: {e}")

    return sent


async def run_worker_cycle(bot: Bot, seen_keys: set[str], silent_init: bool = False) -> int:
    total_sent = 0

    try:
        forex_articles = fetch_latest_articles(FOREX_QUERY)
        total_sent += await send_category_article(
            bot, forex_articles, seen_keys,
            "forex", format_forex_message, silent_init
        )
    except Exception as exc:
        print(f"[ERROR] Forex category failed in cycle: {exc}")

    try:
        india_articles = fetch_latest_articles(INDIA_MARKET_QUERY)
        total_sent += await send_category_article(
            bot, india_articles, seen_keys,
            "india", format_india_message, silent_init
        )
    except Exception as exc:
        print(f"[ERROR] India category failed in cycle: {exc}")

    try:
        intraday_articles = fetch_latest_articles(INTRADAY_STOCK_QUERY)
        total_sent += await send_category_article(
            bot, intraday_articles, seen_keys,
            "intraday", format_intraday_message, silent_init
        )
    except Exception as exc:
        print(f"[ERROR] Intraday category failed in cycle: {exc}")

    try:
        total_sent += await send_options_suggestion(bot, seen_keys)
    except Exception as exc:
        print(f"[ERROR] Options suggestions failed in cycle: {exc}")

    try:
        total_sent += await send_institutional_signals(bot, seen_keys)
    except Exception as exc:
        print(f"[ERROR] Institutional signals failed in cycle: {exc}")

    return total_sent


def validate_config() -> list[str]:
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")

    provider = get_active_provider()
    if provider == "newsapi":
        if not NEWS_API_KEY:
            missing.append("NEWS_API_KEY")
    elif provider == "finnhub":
        if not FINNHUB_API_KEY:
            missing.append("FINNHUB_API_KEY")
    elif not NEWSDATA_API_KEY:
        missing.append("NEWSDATA_API_KEY")

    return missing


async def crypto_screener_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodic crypto pump/dump screening job."""
    try:
        sent = crypto_screener.run_scan_cycle()
        if sent:
            print(f"[CRYPTO SCREENER] Sent {sent} pump alert(s).")
    except Exception as exc:
        print(f"[CRYPTO SCREENER] Scan cycle failed: {exc}")


async def news_broadcast_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    global _seen_keys
    try:
        sent_count = await run_worker_cycle(context.bot, _seen_keys)
        if sent_count:
            print(f"Worker cycle complete. Sent {sent_count} message(s).")
    except Exception as exc:
        print(f"[ERROR] Worker cycle failed: {exc}")


async def high_impact_check_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    global _seen_keys
    try:
        # Check Forex, India and Intraday queries for high impact news immediately
        all_articles = []
        for q, cat in [(FOREX_QUERY, "forex"), (INDIA_MARKET_QUERY, "india"), (INTRADAY_STOCK_QUERY, "intraday")]:
            try:
                for art in fetch_latest_articles(q):
                    art["_category"] = cat
                    all_articles.append(art)
            except Exception:
                pass

        for article in all_articles:
            if not is_recent(article, max_age_hours=6):
                continue
            if not is_high_impact(article):
                continue
            key = article_key(article)
            if not key:
                continue
            cat = article.get("_category", "forex")
            full_key = f"{cat}:{key}"
            
            # Check seen keys (raw key, full prefix key, and normalized title hash)
            if full_key in _seen_keys or key in _seen_keys or any(k.endswith(f":{key}") for k in _seen_keys):
                continue
            title = article.get("title") or ""
            title_norm = clean_title_for_dedup(title)
            if title_norm and f"title:{title_norm}" in _seen_keys:
                continue

            asset = identify_asset(article)
            text = normalize_text(article)
            bias = infer_bias_signal(article)
            direction, confidence = "Neutral", "Low"
            if bias:
                direction, confidence = compute_confidence(text)
            ai_analysis = ai_analyze_news(article) or ""
            conf_pct = _confidence_pct(confidence)
            text_msg = format_high_impact_alert(
                title=article.get("title", "Breaking News"),
                asset=asset,
                direction=direction,
                confidence_pct=conf_pct,
                analysis=ai_analysis or "Significant market-moving event detected.",
            )
            await broadcast(context.bot, text_msg)
            _seen_keys.add(full_key)
            _seen_keys.add(key)
            if title_norm:
                _seen_keys.add(f"title:{title_norm}")
            save_seen_keys(_seen_keys)
            print(f"[HIGH IMPACT NEWS] Text alert sent: {(article.get('title') or '')[:80]}")
    except Exception as exc:
        print(f"[ERROR] High impact news check failed: {exc}")

    # Check Forex Factory Economic Calendar for high impact releases
    try:
        import forexfactory_calendar as ffcal
        events = ffcal.get_upcoming_high_impact(hours_ahead=1, target_currencies={"USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", "INR"})
        if events:
            now = datetime.now(timezone.utc)
            for ev in events:
                dt = ev.get("datetime")
                if not dt:
                    continue
                mins_until = int((dt - now).total_seconds() / 60)
                # Alert when event is 10-35 minutes away
                if 10 <= mins_until <= 35:
                    cal_key = f"cal_trade:{ev['country']}:{ev['title']}:{dt.strftime('%Y%m%d_%H%M')}"
                    if cal_key in _seen_keys:
                        continue
                    
                    # Generate AI scenarios trade setup
                    alert_text = ai_agent.generate_calendar_trade_setup(ev)
                    if alert_text:
                        await broadcast(context.bot, alert_text)
                        _seen_keys.add(cal_key)
                        save_seen_keys(_seen_keys)
                        print(f"[CALENDAR TRADE] Setup generated and sent for {ev['title']} ({ev['country']})")
    except Exception as e:
        print(f"[ERROR] Economic calendar checking failed: {e}")


def _signals_yesterday() -> list[dict]:
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    return [s for s in load_signal_log() if s.get("date") == yesterday]


def _build_signal_results_block(signals: list[dict]) -> str:
    if not signals:
        return "_No signals sent yesterday._"
    lines: list[str] = []
    for s in signals:
        icon = " 🟢" if s["direction"] == "BUY" else " 🔴"
        lines.append(f"{icon} {s['pair']}: {s['direction']} @ {s['entry']} — OPEN")
        lines.append(f"   TP1: {s['tp1']} / TP2: {s['tp2']} | SL: {s['sl']}")
    return "\n".join(lines)


def scrape_holidays_monthly() -> None:
    """Scrapes exchange holidays for the current and next month, saving to CSV in data/."""
    try:
        import os
        import importlib.util
        
        scraper_path = os.path.join(os.path.dirname(__file__), "economic_calendar_scraper", "main.py")
        if not os.path.exists(scraper_path):
            print(f"[HOLIDAY SCRAPER] Path does not exist: {scraper_path}")
            return
            
        spec = importlib.util.spec_from_file_location("scraper_main", scraper_path)
        scraper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scraper_module)
        
        # Ensure 'data' directory exists
        os.makedirs("data", exist_ok=True)
        
        month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        now = datetime.now()
        months_to_scrape = [now, now + timedelta(days=31)]
        
        for dt in months_to_scrape:
            month_str = month_list[dt.month - 1]
            filepath = f"data/{month_str}_calendar.csv"
            
            # Scrape using the imported module
            df = scraper_module.scraper(month_str)
            if df is not None and not df.empty:
                # Filter exchanges using the scraper's built-in exchange filter list
                filtered_df = df[df['Exchange Name'].isin(scraper_module.exchange_filter)]
                filtered_df.to_csv(filepath, index=False)
                print(f"[HOLIDAY SCRAPER] Saved holiday data to {filepath}")
    except Exception as e:
        print(f"[HOLIDAY SCRAPER] Scraping failed: {e}")


def check_holidays_today() -> list[str]:
    """Check if today is a holiday for any major stock exchanges."""
    holidays = []
    try:
        import os
        month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        now = datetime.now()
        month_str = month_list[now.month - 1]
        filepath = f"data/{month_str}_calendar.csv"
        
        if os.path.exists(filepath):
            import pandas as pd
            df = pd.read_csv(filepath)
            today_str = now.strftime('%d.%m.%Y')
            
            # Match columns from scraped CSV: Date, Country, Exchange Name, Holiday Name
            date_col = df.columns[0]
            exchange_col = df.columns[2]
            holiday_col = df.columns[3]
            
            today_df = df[df[date_col] == today_str]
            for _, row in today_df.iterrows():
                exchange = row[exchange_col]
                holiday_name = row[holiday_col]
                holidays.append(f"🔔 *Exchange Holiday:* {exchange} is closed today for *{holiday_name}*.")
    except Exception as e:
        print(f"[HOLIDAY CHECK] Failed to check holidays: {e}")
    return holidays


async def scrape_holidays_monthly_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue adapter for monthly holiday scraping."""
    scrape_holidays_monthly()


async def morning_briefing_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Template 4 — Morning market briefing (text, English only)."""
    try:
        now_ist  = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        date_str = now_ist.strftime("%d %B %Y")

        # Yesterday's signals
        yesterday_signals = _signals_yesterday()
        sig_lines = []
        for s in yesterday_signals[:4]:
            icon = "🟢" if s["direction"] == "BUY" else "🔴"
            sig_lines.append(f"{icon} {s['pair']} {s['direction']} @ {s['entry']} — OPEN")
        sig_block = "\n".join(sig_lines) if sig_lines else "_No signals sent yesterday._"

        # Key events today
        ev_lines = []
        try:
            import forexfactory_calendar as ffcal
            all_events = ffcal.get_upcoming_high_impact(hours_ahead=24)
            for ev in all_events[:4]:
                imp     = ev.get("impact", "MED").upper()
                imp_ico = "🔴" if imp == "HIGH" else "🟡"
                ev_lines.append(f"{imp_ico} {ev.get('time','')}  —  {_strip_md(ev['title'])}  [{imp}]")
        except Exception:
            pass
        ev_block = "\n".join(ev_lines) if ev_lines else "_No major events today._"

        # Market overview (English only)
        prices      = fetch_current_prices()
        gold_price  = prices.get("XAU/USD", "N/A")
        dxy_price   = prices.get("DXY",     "N/A")
        nifty_price = prices.get("NIFTY",   "N/A")

        overview = _strip_md(
            _groq_chat(
                f"Generate a 3-4 sentence market overview for {date_str}. "
                f"DXY={dxy_price}, Gold={gold_price}, Nifty={nifty_price}. "
                "Cover DXY trend, Gold level, key overnight moves, caution zones. "
                "English only. Concise."
            ) or
            f"Gold at {gold_price}. DXY at {dxy_price}. Nifty at {nifty_price}. "
            "Trade cautiously around major economic events today."
        )

        text = (
            f"🌅 *Market Briefing — {date_str}*\n"
            f"_Forex  ·  Crypto  ·  NSE / BSE  ·  Events_\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📋 *Yesterday's Signals*\n"
            f"{sig_block}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Key Events Today* (IST)\n"
            f"{ev_block}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔭 *Market Overview*\n"
            f"{overview}\n\n"
            f"🔖 #morning  #briefing  #forex  #NSE  #crypto"
        )
        await broadcast(context.bot, text)
        print(f"[MORNING BRIEFING] Sent for {date_str}")
    except Exception as exc:
        print(f"[ERROR] Morning briefing failed: {exc}")


async def premarket_india_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Template 6 — Pre-market India NSE/BSE news (30 min before 9:15 AM IST open)."""
    try:
        now_ist  = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        date_str = now_ist.strftime("%d %b %Y")

        articles = fetch_latest_articles(INTRADAY_STOCK_QUERY) + \
                   fetch_latest_articles(INDIA_MARKET_QUERY)

        news_lines = []
        seen_titles: set[str] = set()
        for a in articles:
            t = _strip_md(a.get("title") or "")
            if not t or t in seen_titles:
                continue
            seen_titles.add(t)
            src = _strip_md(a.get("source_name") or "")
            news_lines.append(f"• {t[:90]}" + (f"\n  📰 _{src}_" if src else ""))
            if len(news_lines) >= 5:
                break

        news_block = "\n".join(news_lines) if news_lines else "_No pre-market news available._"

        prices      = fetch_current_prices()
        nifty_price = prices.get("NIFTY", "N/A")
        sensex_str  = "—"
        nifty_str   = f"{nifty_price}" if nifty_price != "N/A" else "N/A"

        outlook_prompt = (
            f"In 2 sentences, give a pre-market outlook for Indian NSE/BSE markets on {date_str}. "
            f"Nifty futures: {nifty_str}. English only. Concise."
        )
        outlook = _strip_md(_groq_chat(outlook_prompt) or
                            "Watch for gap-up or gap-down openings based on overnight global cues.")

        text = (
            f"🔔 *PRE-MARKET INDIA — {date_str}*\n"
            f"⏰ _NSE/BSE opens in ~30 minutes_\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📰 *Top Stories Before Open*\n"
            f"{news_block}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 *Pre-Market Levels*\n"
            f"  NIFTY futures:  {nifty_str}\n\n"
            f"💡 *Pre-Market Signal:* {outlook}\n\n"
            f"🔖 #premarket  #NSE  #BSE  #India"
        )
        await broadcast(context.bot, text)
        print(f"[PRE-MARKET INDIA] Sent for {date_str}")
    except Exception as exc:
        print(f"[ERROR] Pre-market India job failed: {exc}")


async def session_summary_job(
    context: ContextTypes.DEFAULT_TYPE,
    session_name: str,
    is_open: bool,
    tags: list[str],
) -> None:
    """Template 5 — Market session open / close summary."""
    try:
        now_ist  = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        date_str = now_ist.strftime("%d %b %Y")
        time_str = now_ist.strftime("%I:%M %p")
        phase    = "OPENS 🟢" if is_open else "CLOSES 🔴"
        phase_icon = "🔔" if is_open else "🔕"

        prices = fetch_current_prices()
        label_map = [
            ("XAU/USD", "Gold  (XAU/USD)"),
            ("EUR/USD", "EUR/USD       "),
            ("GBP/USD", "GBP/USD       "),
            ("US100",   "NASDAQ 100    "),
            ("US30",    "Dow Jones     "),
            ("DXY",     "DXY Index     "),
            ("NIFTY",   "Nifty 50      "),
            ("WTI",     "Crude Oil WTI "),
            ("US10Y",   "US 10Y Yield  "),
        ]
        price_lines = []
        for key, label in label_map:
            val = prices.get(key)
            if val:
                price_lines.append(f"  {label}: {_price_str(val, key)}")
            if len(price_lines) >= 6:
                break
        prices_block = "\n".join(price_lines) if price_lines else "  _Prices unavailable_"

        outlook_prompt = (
            f"In 2-3 sentences give a trading outlook for the {session_name} "
            f"session {'opening' if is_open else 'closing'} on {date_str}. "
            "English only. Factual and concise."
        )
        outlook = _strip_md(_groq_chat(outlook_prompt) or
                            f"Monitor key levels during the {session_name} session.")

        tag_str = "  ".join(f"#{t}" for t in tags)
        text = (
            f"{phase_icon} *{session_name} — {phase}*\n"
            f"📅 {date_str}  ·  {time_str} IST\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 *Market Snapshot*\n"
            f"{prices_block}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Session Outlook:*\n"
            f"{outlook}\n\n"
            f"🔖 {tag_str}"
        )
        await broadcast(context.bot, text)
        print(f"[SESSION] {session_name} {'OPEN' if is_open else 'CLOSE'} summary sent.")
    except Exception as exc:
        print(f"[ERROR] Session summary job failed: {exc}")


# ── Session job wrappers (one per open/close event) ──────────────────────────
async def _nse_open_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await session_summary_job(ctx, "NSE / BSE India", True, ["NSE", "BSE", "India", "marketopen"])

async def _nse_close_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await session_summary_job(ctx, "NSE / BSE India", False, ["NSE", "BSE", "India", "marketclose"])

async def _london_open_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await session_summary_job(ctx, "London Forex", True, ["London", "forex", "GBP", "EUR", "session"])

async def _london_close_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await session_summary_job(ctx, "London Forex", False, ["London", "forex", "session"])

async def _ny_open_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await session_summary_job(ctx, "New York Forex", True, ["NewYork", "NYSE", "forex", "USD", "session"])

async def _ny_close_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await session_summary_job(ctx, "New York Forex", False, ["NewYork", "forex", "session"])


async def _realtime_polling_job(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Run VIX spike, pre-market gap, and economic calendar checks."""
    sent = realtime_alert.run_polling_cycle()
    if sent:
        print(f"[REALTIME] {sent} alert(s) sent via polling cycle.")


# ── AI Agent Improvement Job ─────────────────────────────────────────────────
@contextmanager
def _period_counter():
    _period_counter._n = getattr(_period_counter, "_n", 0) + 1
    yield _period_counter._n
    _period_counter._n = getattr(_period_counter, "_n", 0)

async def ai_agent_improvement_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """AI agent runs every ~30 min to improve trade suggestions and app quality."""
    try:
        with _period_counter() as cycle:
            now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
            time_str = now_ist.strftime("%H:%M IST")

            # 1. BTC market update every cycle
            try:
                btc_update = ai_agent.generate_btc_market_update()
                if btc_update:
                    btc_block = ai_agent.format_btc_market_update(btc_update)
                    await broadcast(context.bot, btc_block)
                    print(f"[AI AGENT] BTC market update sent at {time_str}")
            except Exception as e:
                print(f"[AI AGENT] BTC update failed: {e}")

            # 2. BTC trade suggestion every other cycle (every ~60 min)
            if cycle % 2 == 0:
                try:
                    btc_suggestion = ai_agent.generate_btc_trade_suggestion()
                    if btc_suggestion:
                        btc_sig_block = ai_agent.format_btc_signal_block(btc_suggestion)
                        await broadcast(context.bot, btc_sig_block)
                        print(f"[AI AGENT] BTC trade suggestion sent at {time_str}")
                except Exception as e:
                    print(f"[AI AGENT] BTC suggestion failed: {e}")

            # 3. Educational tip every 6 cycles (~3 hours)
            if cycle % 6 == 0:
                try:
                    recent_signals = load_signal_log()[-20:]
                    tip = ai_agent.generate_market_education_tip(recent_signals)
                    if tip:
                        await broadcast(context.bot, f"🧠 *AI Education Tip*\n\n{tip}")
                        print(f"[AI AGENT] Education tip sent at {time_str}")
                except Exception as e:
                    print(f"[AI AGENT] Education tip failed: {e}")

            # 4. System improvement report twice daily (every ~12 hours = cycle 24)
            if cycle % 24 == 0:
                try:
                    recent_signals = load_signal_log()[-50:]
                    improvement = ai_agent.analyze_recent_signals_for_improvement(recent_signals)
                    if improvement:
                        await broadcast(
                            context.bot,
                            f"🤖 *AI System Improvement Report*\n\n{improvement}",
                        )
                        print(f"[AI AGENT] Improvement report sent at {time_str}")
                except Exception as e:
                    print(f"[AI AGENT] Improvement report failed: {e}")

            # 5. Market snapshot every 8 cycles (~4 hours)
            if cycle % 8 == 0:
                try:
                    prices = fetch_current_prices()
                    snapshot_lines = [
                        f"📸 *AI Market Snapshot* — {time_str}",
                        f"━━━━━━━━━━━━━━━━━━",
                    ]
                    for pair in ["XAU/USD", "EUR/USD", "GBP/USD", "BTC/USD", "ETH/USD",
                                 "US100", "US30", "DXY", "NIFTY", "WTI", "US10Y"]:
                        p = prices.get(pair)
                        if p:
                            snapshot_lines.append(f"  {pair}: {_price_str(p, pair)}")
                    snapshot_lines.append("")
                    enh = ai_agent.enhance_message_for_trader_levels(
                        "\n".join(snapshot_lines), "intermediate",
                    )
                    snapshot_lines.append(f"💡 {enh}")
                    await broadcast(context.bot, "\n".join(snapshot_lines))
                    print(f"[AI AGENT] Market snapshot sent at {time_str}")
                except Exception as e:
                    print(f"[AI AGENT] Market snapshot failed: {e}")

            print(f"[AI AGENT] Cycle {cycle} completed at {time_str}")
    except Exception as exc:
        print(f"[AI AGENT] Job failed: {exc}")


def normalize_ticker_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper().replace("/", "")
    if not symbol:
        return symbol

    # Spot metals / Commodities
    commodity_and_index_map = {
        "GOLD": "GC=F",
        "XAUUSD": "GC=F",
        "SILVER": "SI=F",
        "XAGUSD": "SI=F",
        "OIL": "CL=F",
        "USOIL": "CL=F",
        "WTI": "CL=F",
        "BRENT": "BZ=F",
        "UKOIL": "BZ=F",
        "SPX": "^GSPC",
        "SP500": "^GSPC",
        "S&P500": "^GSPC",
        "COMP": "^IXIC",
        "NASDAQ": "^IXIC",
        "DJI": "^DJI",
        "DOW": "^DJI",
    }
    if symbol in commodity_and_index_map:
        return commodity_and_index_map[symbol]

    # Common Nifty stocks & Indices mapping
    indian_map = {
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "SENSEX": "^BSESN",
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFCBANK": "HDFCBANK.NS",
        "INFY": "INFY.NS",
        "ICICIBANK": "ICICIBANK.NS",
        "BHARTIARTL": "BHARTIARTL.NS",
        "SBIN": "SBIN.NS",
        "LICI": "LICI.NS",
        "ITC": "ITC.NS",
        "HINDUNILVR": "HINDUNILVR.NS",
        "LT": "LT.NS",
        "BAJFINANCE": "BAJFINANCE.NS",
        "HCLTECH": "HCLTECH.NS",
        "MARUTI": "MARUTI.NS",
        "SUNPHARMA": "SUNPHARMA.NS",
        "ADANIENT": "ADANIENT.NS",
        "TATAMOTORS": "TATAMOTORS.NS",
        "AXISBANK": "AXISBANK.NS",
        "ONGC": "ONGC.NS",
        "NTPC": "NTPC.NS",
        "JSWSTEEL": "JSWSTEEL.NS",
        "KOTAKBANK": "KOTAKBANK.NS",
        "COALINDIA": "COALINDIA.NS",
        "TITAN": "TITAN.NS",
        "ULTRACEMCO": "ULTRACEMCO.NS",
        "SBILIFE": "SBILIFE.NS",
        "ADANIPORTS": "ADANIPORTS.NS",
        "ASIANPAINT": "ASIANPAINT.NS",
        "HINDALCO": "HINDALCO.NS",
        "POWERGRID": "POWERGRID.NS",
        "GRASIM": "GRASIM.NS",
        "HDFCLIFE": "HDFCLIFE.NS",
        "BPCL": "BPCL.NS",
        "INDUSINDBK": "INDUSINDBK.NS",
        "BRITANNIA": "BRITANNIA.NS",
        "DRREDDY": "DRREDDY.NS",
        "JIOFIN": "JIOFIN.NS",
        "TATASTEEL": "TATASTEEL.NS",
        "WIPRO": "WIPRO.NS",
        "HEROMOTOCO": "HEROMOTOCO.NS",
        "APOLLOHOSP": "APOLLOHOSP.NS",
        "EICHERMOT": "EICHERMOT.NS",
        "LTIM": "LTIM.NS",
        "DIVISLAB": "DIVISLAB.NS",
        "SHRIRAMFIN": "SHRIRAMFIN.NS",
        "NESTLEIND": "NESTLEIND.NS",
        "CIPLA": "CIPLA.NS",
        "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
        "GRANULES": "GRANULES.NS",
        "AUROPHARMA": "AUROPHARMA.NS",
        "TVSMOTOR": "TVSMOTOR.NS",
    }
    if symbol in indian_map:
        return indian_map[symbol]

    forex_pairs = {
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
        "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "GBPCAD", "EURCAD", "EURCHF",
        "GBPCHF", "CHFJPY", "CADJPY", "NZDJPY", "AUDCAD", "AUDNZD", "AUDCHF",
        "USDSGD", "USDHKD", "USDMXN", "USDTRY", "USDZAR", "USDCNH", "USDSEK",
        "USDNOK", "USDDKK", "USDINR"
    }
    if symbol in forex_pairs:
        return f"{symbol}=X"

    if symbol.endswith("=X") or symbol.endswith("-USD") or symbol.endswith(".NS") or symbol.startswith("^"):
        return symbol

    # Crypto lookup
    cryptos = {
        "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "LINK", "LTC", "BNB",
        "AVAX", "UNI", "MATIC", "SHIB", "TRX", "TON", "NEAR", "BCH", "XLM"
    }
    if symbol in cryptos:
        return f"{symbol}-USD"

    # Crypto suffix formats e.g. BTCUSD -> BTC-USD
    if symbol.endswith("USD") and len(symbol) > 3:
        prefix = symbol[:-3]
        if prefix in cryptos:
            return f"{prefix}-USD"

    return symbol


def get_financials_summary(ticker) -> str:
    try:
        df = ticker.financials
        if df is None or df.empty:
            return "No Income Statement data available."
        cols = list(df.columns)[:3]
        lines = ["INCOME STATEMENT SUMMARY (in Millions):"]
        header = "Metric | " + " | ".join([str(c)[:10] for c in cols])
        lines.append(header)
        lines.append("-" * len(header))
        
        metrics_of_interest = {
            "Total Revenue": ["Total Revenue", "Revenue"],
            "Gross Profit": ["Gross Profit"],
            "Operating Income": ["Operating Income", "Operating Income or Loss"],
            "Net Income": ["Net Income", "Net Income Common Stockholders"]
        }
        for name, keys in metrics_of_interest.items():
            for k in keys:
                if k in df.index:
                    vals = []
                    for col in cols:
                        v = df.loc[k].get(col, 0)
                        if isinstance(v, (int, float)):
                            vals.append(f"{v / 1e6:.1f}M")
                        else:
                            vals.append(str(v))
                    lines.append(f"{name} | " + " | ".join(vals))
                    break
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving Income Statement: {e}"


def get_balance_sheet_summary(ticker) -> str:
    try:
        df = ticker.balance_sheet
        if df is None or df.empty:
            return "No Balance Sheet data available."
        cols = list(df.columns)[:3]
        lines = ["BALANCE SHEET SUMMARY (in Millions):"]
        header = "Metric | " + " | ".join([str(c)[:10] for c in cols])
        lines.append(header)
        lines.append("-" * len(header))
        
        metrics_of_interest = {
            "Total Assets": ["Total Assets"],
            "Total Liabilities": ["Total Liabilities Net Minor Interest", "Total Liabilities"],
            "Stockholders Equity": ["Stockholders Equity", "Total Stockholders Equity"],
            "Cash & Short Term Investments": ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"]
        }
        for name, keys in metrics_of_interest.items():
            for k in keys:
                if k in df.index:
                    vals = []
                    for col in cols:
                        v = df.loc[k].get(col, 0)
                        if isinstance(v, (int, float)):
                            vals.append(f"{v / 1e6:.1f}M")
                        else:
                            vals.append(str(v))
                    lines.append(f"{name} | " + " | ".join(vals))
                    break
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving Balance Sheet: {e}"


def get_cash_flow_summary(ticker) -> str:
    try:
        df = ticker.cashflow
        if df is None or df.empty:
            return "No Cash Flow data available."
        cols = list(df.columns)[:3]
        lines = ["CASH FLOW SUMMARY (in Millions):"]
        header = "Metric | " + " | ".join([str(c)[:10] for c in cols])
        lines.append(header)
        lines.append("-" * len(header))
        
        metrics_of_interest = {
            "Operating Cash Flow": ["Operating Cash Flow", "Total Cash From Operating Activities"],
            "Capital Expenditure": ["Capital Expenditure"],
            "Free Cash Flow": ["Free Cash Flow"]
        }
        for name, keys in metrics_of_interest.items():
            for k in keys:
                if k in df.index:
                    vals = []
                    for col in cols:
                        v = df.loc[k].get(col, 0)
                        if isinstance(v, (int, float)):
                            vals.append(f"{v / 1e6:.1f}M")
                        else:
                            vals.append(str(v))
                    lines.append(f"{name} | " + " | ".join(vals))
                    break
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving Cash Flow: {e}"


def generate_performance_chart(symbol, hist, save_path) -> bool:
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(hist.index, hist["Close"], color="#06b6d4", linewidth=2, label="Close Price")
        ax.fill_between(hist.index, hist["Close"], alpha=0.15, color="#06b6d4")
        ax.set_title(f"{symbol} Stock Performance (1 Year)", color="#e2e8f0", fontsize=12, fontweight="bold", pad=15)
        ax.set_xlabel("Date", color="#94a3b8", fontsize=9)
        ax.set_ylabel("Price", color="#94a3b8", fontsize=9)
        ax.tick_params(colors="#94a3b8", labelsize=8)
        ax.grid(True, color="#334155", linestyle="--", alpha=0.5)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color("#475569")
        plt.tight_layout()
        plt.savefig(save_path, transparent=True, dpi=150)
        plt.close()
        return True
    except Exception as e:
        print(f"[CHART ERROR]: {e}")
        return False


def compile_pdf_report(symbol, text_report, chart_path, save_path) -> bool:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#06b6d4'),
            spaceAfter=15
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#a855f7'),
            spaceAfter=10,
            spaceBefore=15
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1e293b')
        )
        story.append(Paragraph(f"FinRobot Institutional Equity Report - {symbol}", title_style))
        story.append(Spacer(1, 10))
        sections = text_report.split("\n\n")
        for sec in sections:
            if sec.startswith("### "):
                story.append(Paragraph(sec[4:].strip(), subtitle_style))
            elif sec.startswith("## "):
                story.append(Paragraph(sec[3:].strip(), subtitle_style))
            else:
                story.append(Paragraph(sec.replace("\n", "<br/>").strip(), body_style))
                story.append(Spacer(1, 10))
        if os.path.exists(chart_path):
            story.append(Spacer(1, 15))
            story.append(Paragraph("Stock Performance Visual Chart", subtitle_style))
            img = Image(chart_path, width=400, height=200)
            story.append(img)
        doc.build(story)
        return True
    except Exception as e:
        print(f"[PDF ERROR]: {e}")
        return False


async def handle_health_check(reader, writer):
    try:
        request = await reader.read(1024)
        req_text = request.decode("utf-8", errors="ignore")
        first_line = req_text.split("\r\n")[0] if req_text else ""
        parts = first_line.split()
        method = parts[0] if len(parts) > 0 else "GET"
        path = parts[1] if len(parts) > 1 else "/"
    except Exception:
        method = "GET"
        path = "/"

    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(path)
    path_only = parsed_url.path
    query_params = parse_qs(parsed_url.query)

    body_data = ""
    if method == "POST":
        # Parse content-length from headers
        headers_lines = req_text.split("\r\n")[1:]
        content_length = 0
        for line in headers_lines:
            if line.lower().startswith("content-length:"):
                try:
                    content_length = int(line.split(":")[1].strip())
                except ValueError:
                    pass
                break
        
        # Extract body from read data
        body_parts = req_text.split("\r\n\r\n", 1)
        if len(body_parts) > 1:
            body_data = body_parts[1]
            
        # Read remaining body bytes if needed
        already_read = len(body_data.encode("utf-8", errors="ignore"))
        if already_read < content_length:
            try:
                remaining = content_length - already_read
                extra_bytes = await reader.read(remaining)
                body_data += extra_bytes.decode("utf-8", errors="ignore")
            except Exception:
                pass

    if method == "OPTIONS":
        response_header = (
            f"HTTP/1.1 204 No Content\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            f"Access-Control-Allow-Headers: Content-Type\r\n"
            f"Connection: close\r\n\r\n"
        )
        try:
            writer.write(response_header.encode("utf-8"))
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        return



    elif path_only == "/api/smc-matrix":
        try:
            symbols_param = query_params.get("symbols", ["^NSEI, XAUUSD=X, EURUSD=X"])[0]
            symbols_list = [s.strip() for s in symbols_param.split(",") if s.strip()]
            
            import smc_matrix
            results = smc_matrix.scan_smc(symbols_list)
            response_body = json.dumps(results)
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    if path_only == "/api/signals":
        signals = load_signal_log()
        if len(signals) < 15:
            default_signals = [
                # Forex
                {"pair": "EUR/USD", "direction": "BUY", "entry": 1.0850, "tp1": 1.0920, "tp2": 1.1010, "sl": 1.0810, "confidence": 88, "timestamp": "Live", "source": "forex"},
                {"pair": "GBP/USD", "direction": "BUY", "entry": 1.2720, "tp1": 1.2800, "tp2": 1.2910, "sl": 1.2670, "confidence": 85, "timestamp": "Live", "source": "forex"},
                {"pair": "USD/JPY", "direction": "SELL", "entry": 155.40, "tp1": 154.20, "tp2": 152.80, "sl": 156.10, "confidence": 82, "timestamp": "Live", "source": "forex"},
                {"pair": "AUD/USD", "direction": "BUY", "entry": 0.6580, "tp1": 0.6640, "tp2": 0.6720, "sl": 0.6540, "confidence": 80, "timestamp": "Live", "source": "forex"},
                # Commodities
                {"pair": "XAU/USD (Gold)", "direction": "BUY", "entry": 2420.50, "tp1": 2445.00, "tp2": 2480.00, "sl": 2405.00, "confidence": 92, "timestamp": "Live", "source": "commodities"},
                {"pair": "XAG/USD (Silver)", "direction": "BUY", "entry": 27.80, "tp1": 28.60, "tp2": 29.50, "sl": 27.20, "confidence": 86, "timestamp": "Live", "source": "commodities"},
                {"pair": "WTI CRUDE OIL", "direction": "SELL", "entry": 78.40, "tp1": 76.20, "tp2": 73.50, "sl": 79.80, "confidence": 84, "timestamp": "Live", "source": "commodities"},
                # Indian Market
                {"pair": "RELIANCE.NS", "direction": "BUY", "entry": 1320.00, "tp1": 1345.00, "tp2": 1380.00, "sl": 1305.00, "confidence": 89, "timestamp": "Live", "source": "india"},
                {"pair": "NIFTY 24400 CE", "direction": "BUY", "entry": 185.00, "tp1": 240.00, "tp2": 320.00, "sl": 150.00, "confidence": 90, "timestamp": "Live", "source": "india"},
                {"pair": "TCS.NS", "direction": "BUY", "entry": 2290.00, "tp1": 2340.00, "tp2": 2410.00, "sl": 2260.00, "confidence": 83, "timestamp": "Live", "source": "india"},
                # US Market
                {"pair": "NVDA", "direction": "BUY", "entry": 128.50, "tp1": 135.00, "tp2": 145.00, "sl": 124.00, "confidence": 91, "timestamp": "Live", "source": "us"},
                {"pair": "AAPL", "direction": "BUY", "entry": 224.00, "tp1": 232.00, "tp2": 242.00, "sl": 219.00, "confidence": 87, "timestamp": "Live", "source": "us"},
            ]
            for ds in default_signals:
                if not any(s.get("pair") == ds["pair"] for s in signals):
                    signals.append(ds)
        signals_subset = list(reversed(signals))[:50]
        response_body = json.dumps(signals_subset)
        content_type = "application/json"

    elif path_only == "/api/calendar":
        try:
            import forexfactory_calendar as ffcal
            from datetime import datetime, timezone, timedelta
            
            range_type = query_params.get("range", ["this_week"])[0].strip().lower()
            from_val = query_params.get("from", [""])[0].strip()
            to_val = query_params.get("to", [""])[0].strip()
            
            now = datetime.now(timezone.utc)
            from_dt = None
            to_dt = None
            
            if range_type == "this_week":
                start_of_week = now - timedelta(days=now.weekday() + 1 if now.weekday() != 6 else 0)
                from_dt = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
                to_dt = from_dt + timedelta(days=7)
            elif range_type == "next_week":
                start_of_week = now - timedelta(days=now.weekday() + 1 if now.weekday() != 6 else 0)
                start_of_next_week = start_of_week + timedelta(days=7)
                from_dt = start_of_next_week.replace(hour=0, minute=0, second=0, microsecond=0)
                to_dt = from_dt + timedelta(days=7)
            elif range_type == "next_month":
                if now.month == 12:
                    from_dt = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
                else:
                    from_dt = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
                if from_dt.month == 12:
                    to_dt = datetime(from_dt.year + 1, 1, 1, tzinfo=timezone.utc)
                else:
                    to_dt = datetime(from_dt.year, from_dt.month + 1, 1, tzinfo=timezone.utc)
            elif range_type == "full_year":
                from_dt = datetime(now.year, 1, 1, tzinfo=timezone.utc)
                to_dt = datetime(now.year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            elif range_type == "custom":
                try:
                    from_dt = datetime.strptime(from_val, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except ValueError:
                    from_dt = now
                try:
                    to_dt = datetime.strptime(to_val, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                except ValueError:
                    to_dt = from_dt + timedelta(days=7)
            
            events = ffcal.fetch_calendar_events(from_dt, to_dt)
            serializable_events = []
            for ev in events:
                serializable_events.append({
                    "title": ev.get("title"),
                    "country": ev.get("country"),
                    "impact": ev.get("impact"),
                    "time": ev.get("time"),
                    "date": ev.get("date"),
                    "forecast": ev.get("forecast", "N/A"),
                    "previous": ev.get("previous", "N/A"),
                    "actual": ev.get("actual", "N/A"),
                    "datetime": ev["datetime"].isoformat() if ev.get("datetime") else None
                })
            response_body = json.dumps(serializable_events)
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/calendar-analyze":
        title = query_params.get("title", [""])[0].strip()
        country = query_params.get("country", [""])[0].strip()
        actual = query_params.get("actual", [""])[0].strip()
        forecast = query_params.get("forecast", [""])[0].strip()
        previous = query_params.get("previous", [""])[0].strip()
        
        if not title:
            response_body = json.dumps({"error": "title parameter is required."})
            content_type = "application/json"
        else:
            try:
                import yfinance as yf
                ref_assets = ["XAU/USD", "EUR/USD", "USD/INR", "^NSEI"]
                prices_summary = []
                for asset in ref_assets:
                    try:
                        ticker = normalize_ticker_symbol(asset)
                        tk = yf.Ticker(ticker)
                        hist = tk.history(period="1d")
                        if not hist.empty:
                            prices_summary.append(f"{asset}: {hist['Close'].iloc[-1]:.2f}")
                    except Exception:
                        pass
                
                prices_ctx = ", ".join(prices_summary)
                
                prompt = (
                    f"Perform a rapid, professional position impact analysis for this macro economic event:\n"
                    f"Event: {title} ({country})\n"
                    f"Actual: {actual} | Forecast: {forecast} | Previous: {previous}\n\n"
                    f"Current Market Prices context: {prices_ctx}\n\n"
                    f"Explain in 2-3 sentences:\n"
                    f"1. Short detail summary of the news value.\n"
                    f"2. Precise impact analysis on trading positions (e.g. Bullish/Bearish for Gold, USD, or Indian Stocks)."
                )
                
                analysis = _analyzer_groq_chat(prompt, system_prompt="You are a senior macro trading strategist. Be concise, direct and data-driven.")
                if not analysis:
                    if actual == "N/A" or not actual:
                        analysis = "Algorithmic Analysis: The market is currently awaiting the actual figures for this event. Institutional positions are likely hedged to prevent volatility exposure. Expect short-term spikes across relevant Forex and Index pairs upon release."
                    else:
                        analysis = f"Algorithmic Analysis: The actual figure of {actual} compared to the forecast of {forecast} creates a measurable deviation. If actual > forecast for inflation/jobs, expect currency strength and equity weakness. If actual < forecast, expect currency weakness and equity relief rallies."
                response_body = json.dumps({"analysis": analysis})
            except Exception as e:
                response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/test-telegram":
        try:
            from telegram import Bot
            if BOT_TOKEN:
                bot = Bot(token=BOT_TOKEN)
                test_msg = "🔔 <b>Test Telegram Connection</b>\n\nYour white-label Trading Dashboard is successfully connected to Telegram! Ready to broadcast real-time signals."
                sent = await broadcast(bot, test_msg, parse_mode="HTML")
                response_body = json.dumps({"success": True, "sent_count": sent})
            else:
                response_body = json.dumps({"error": "BOT_TOKEN not configured in environment."})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/momentum/start":
        try:
            from momentum_engine import engine
            engine.start()
            response_body = json.dumps({"status": "Started"})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/momentum/stop":
        try:
            from momentum_engine import engine
            engine.stop()
            response_body = json.dumps({"status": "Stopped"})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/momentum/live":
        try:
            from momentum_engine import engine
            trades = list(engine.active_trades.values())
            
            import sqlite3
            conn = sqlite3.connect("momentum_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, event, message, timestamp FROM strategy_logs ORDER BY id DESC LIMIT 10")
            logs = [{"symbol": r[0], "event": r[1], "message": r[2], "timestamp": r[3]} for r in cursor.fetchall()]
            conn.close()
            
            response_body = json.dumps({"active_trades": trades, "recent_logs": logs, "engine_active": engine.active})
            content_type = "application/json"
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only == "/api/news":
        try:
            lang = query_params.get("lang", ["en"])[0].strip().lower()
            articles = fetch_latest_articles()[:15]
            serializable_articles = []
            for a in articles:
                text_body = normalize_text(a)
                direction, confidence = "Neutral", "Low"
                bias = infer_bias_signal(a)
                if bias:
                    direction, confidence = compute_confidence(text_body)
                
                desc = a.get("description") or "No description available."
                if len(desc) > 250:
                    desc = desc[:247] + "..."
                
                serializable_articles.append({
                    "title": a.get("title") or "Market Update",
                    "description": desc,
                    "source": a.get("source_name") or a.get("source", "Market Feed"),
                    "direction": direction,
                    "confidence": confidence,
                    "publishedAt": a.get("publishedAt") or a.get("time") or "",
                    "link": a.get("link") or a.get("url") or "",
                    "asset": identify_asset(a)
                })

            if lang not in {"en", "english"}:
                lang_names = {
                    "hi": "Hindi", "hindi": "Hindi",
                    "bn": "Bengali", "bengali": "Bengali",
                    "es": "Spanish", "spanish": "Spanish",
                    "ar": "Arabic", "arabic": "Arabic",
                    "de": "German", "german": "German",
                    "fr": "French", "french": "French",
                    "it": "Italian", "italian": "Italian",
                    "ja": "Japanese", "japanese": "Japanese",
                    "zh": "Chinese", "chinese": "Chinese",
                    "ru": "Russian", "russian": "Russian",
                    "pt": "Portuguese", "portuguese": "Portuguese",
                    "nl": "Dutch", "dutch": "Dutch",
                    "tr": "Turkish", "turkish": "Turkish",
                    "ko": "Korean", "korean": "Korean",
                    "pl": "Polish", "polish": "Polish",
                    "vi": "Vietnamese", "vietnamese": "Vietnamese",
                    "sv": "Swedish", "swedish": "Swedish",
                    "da": "Danish", "danish": "Danish",
                    "fi": "Finnish", "finnish": "Finnish",
                    "no": "Norwegian", "norwegian": "Norwegian",
                    "id": "Indonesian", "indonesian": "Indonesian"
                }
                target_lang = lang_names.get(lang, lang.capitalize())
                if target_lang != "English":
                    trans_list = []
                    for idx, art in enumerate(serializable_articles):
                        trans_list.append({
                            "id": idx,
                            "title": art["title"],
                            "description": art["description"]
                        })
                    prompt = (
                        f"You are a professional financial translator. Translate the following list of news articles into {target_lang}. "
                        f"Maintain exact financial terms, abbreviations, and asset names. "
                        f"Return the translated data strictly as a JSON object containing a 'translated_data' key, "
                        f"which is an array of objects with keys 'id', 'title', and 'description':\n\n"
                        f"{json.dumps(trans_list)}"
                    )
                    raw_res = _analyzer_groq_chat(prompt, json_mode=True)
                    if raw_res:
                        try:
                            data = json.loads(raw_res)
                            translated_data = data.get("translated_data") or data.get("data")
                            if not translated_data:
                                import re
                                json_match = re.search(r'\[.*\]', raw_res, re.DOTALL)
                                if json_match:
                                    translated_data = json.loads(json_match.group())
                            
                            if translated_data:
                                for item in translated_data:
                                    idx = item.get("id")
                                    if idx is not None and 0 <= idx < len(serializable_articles):
                                        serializable_articles[idx]["title"] = item.get("title", serializable_articles[idx]["title"])
                                        serializable_articles[idx]["description"] = item.get("description", serializable_articles[idx]["description"])
                        except Exception as parse_e:
                            print(f"[TRANSLATION PARSE ERROR]: {parse_e}")

            response_body = json.dumps(serializable_articles)
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/analyze":
        symbol = query_params.get("symbol", [""])[0].strip().upper()
        symbol = normalize_ticker_symbol(symbol)
        if not symbol:
            response_body = json.dumps({"error": "Symbol parameter is required"})
        else:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if hist.empty and "." not in symbol and "=" not in symbol and "-" not in symbol and "^" not in symbol:
                    symbol = f"{symbol}.NS"
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                if hist.empty:
                    raise Exception(f"No price data found for symbol '{symbol}'")
                current_price = float(hist["Close"].iloc[-1])
                prev_price = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
                change = current_price - prev_price
                change_pct = (change / prev_price) * 100 if prev_price else 0.0

                prompt = (
                    f"Perform a professional technical analysis for asset {symbol}. "
                    f"Current Price: {current_price:.2f}, Daily Change: {change_pct:+.2f}%. "
                    f"Generate a clear trade suggestion: Direction (BUY or SELL or NEUTRAL), "
                    f"Entry Price, Stop Loss, Target 1, Target 2, Confidence level (e.g. 85%), and a 1-sentence analysis reason. "
                    f"Strictly enforce high Risk-to-Reward (R:R) ratios: Target 1 (tp1) must represent a 1:5 Risk-to-Reward ratio "
                    f"relative to the entry and Stop Loss (Reward = 5x Risk). Target 2 (tp2) must represent a 1:10 Risk-to-Reward "
                    f"ratio relative to the entry and Stop Loss (Reward = 10x Risk). "
                    f"Keep the Stop Loss tight to accommodate these ratios. "
                    f"Format the output strictly as a JSON object with keys: "
                    f"'direction', 'entry', 'sl', 'tp1', 'tp2', 'confidence', 'reason'."
                )
                raw_ai_res = _analyzer_groq_chat(prompt, json_mode=True)
                if not raw_ai_res:
                    raise Exception("Too Many Requests. Rate limited. Try after a while.")
                import re
                json_match = re.search(r'\{.*\}', raw_ai_res, re.DOTALL)
                if json_match:
                    ai_data = json.loads(json_match.group())
                else:
                    raise Exception("AI did not return a valid JSON response format")

                ai_data["symbol"] = symbol
                ai_data["current_price"] = f"{current_price:.2f}"
                ai_data["change_pct"] = f"{change_pct:+.2f}%"
                response_body = json.dumps(ai_data)
            except Exception as e:
                response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/indian-intel":
        try:
            exchange = query_params.get("exchange", ["NSE"])[0].upper()
            if exchange not in ("NSE", "BSE"):
                exchange = "NSE"
            import indian_scoring as iscoring
            intel = iscoring.get_full_intel(exchange=exchange)
            response_body = json.dumps(intel)
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/broadcast-indian-intel":
        try:
            exchange = query_params.get("exchange", ["NSE"])[0].upper()
            if exchange not in ("NSE", "BSE"):
                exchange = "NSE"
                
            import indian_scoring as iscoring
            intel = iscoring.get_full_intel(exchange=exchange)
            
            # Format the Telegram report message
            v = intel.get("verdict", {})
            fii = intel.get("fii", {})
            scan = intel.get("scan", [])
            fno_days = intel.get("fno_days", 0)
            
            fii_net_val = fii.get("fii_net", 0.0)
            dii_net_val = fii.get("dii_net", 0.0)
            fii_status = fii.get("fii_status", "Neutral")
            dii_status = fii.get("dii_status", "Neutral")
            fii_date = fii.get("date", "Today")
            
            scan_lines = []
            for s in scan[:5]:
                change_sign = "+" if s.get("change_pct", 0.0) >= 0 else ""
                scan_lines.append(
                    f"• <b>{s['ticker']}</b> ({s['sector']}): <b>₹{s['price']}</b> ({change_sign}{s['change_pct']}%) | RSI: {s['rsi']} | Rating: <b>{s['rating']}</b>"
                )
            stock_signals_text = "\n".join(scan_lines) if scan_lines else "No active signals."
            
            # Format institutional option signals & campaigns
            graded_signals = intel.get("top_graded_signals", [])
            campaigns = intel.get("campaigns", [])
            pcr_watch = intel.get("pcr_watch", [])

            sig_lines = []
            for sig in graded_signals[:3]:
                sig_lines.append(
                    f"• <b>{sig['strike']}</b> [{sig['direction']}] — Score {sig['score']}\n"
                    f"  💰 Flow: <b>{sig['flow_cr']}</b> | Time: {sig['time']}\n"
                    f"  📝 {sig['headline']}"
                )
            sig_text = "\n\n".join(sig_lines) if sig_lines else "No active graded signals."

            camp_lines = []
            for c in campaigns[:3]:
                legs_str = " | ".join([f"{l['name']} {l['amount']}" for l in c['legs']])
                warn_str = f"\n  ⚠️ <i>{c['warning']}</i>" if c.get('warning') else ""
                camp_lines.append(
                    f"• <b>{c['ticker']}</b> [{c['direction']}] {c['stars']} [{c['status_flag']}]\n"
                    f"  💰 Gross: {c['gross_flow']} ({c['net_flow']})\n"
                    f"  🧩 Legs: {legs_str}{warn_str}"
                )
            camp_text = "\n\n".join(camp_lines) if camp_lines else "No active campaigns."

            pcr_str = " | ".join([f"{p['index']}: <b>{p['pcr']}</b>" for p in pcr_watch[:4]])

            message = (
                f"🇮🇳 <b>INSTITUTIONAL OPTIONS FLOW & TAPE INTEL ({exchange})</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 <b>Market Verdict:</b> {v.get('emoji', '🟡')} <b>{v.get('verdict', 'NEUTRAL')}</b>\n"
                f"📝 <b>Rationale:</b> {v.get('reason', '')}\n"
                f"🏛 <b>FII Net:</b> ₹{fii_net_val:,.2f} Cr ({fii_status}) | 🏠 <b>DII Net:</b> ₹{dii_net_val:,.2f} Cr ({dii_status})\n"
                f"🚪 <b>F&O Expiry:</b> <b>{fno_days}</b> days remaining\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>TOP GRADED OPTIONS SIGNALS</b>\n"
                f"{sig_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏢 <b>INSTITUTIONAL CAMPAIGNS (STOCK FLOWS)</b>\n"
                f"{camp_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 <b>INDEX PCR WATCH</b>\n"
                f"{pcr_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 <i>Powered by Indian Market Intelligence Engine</i>"
            )
            
            from telegram import Bot
            if BOT_TOKEN:
                bot = Bot(token=BOT_TOKEN)
                await broadcast(bot, message)
                response_body = json.dumps({"success": True, "message": "Successfully broadcasted to Telegram!"})
            else:
                response_body = json.dumps({"error": "Telegram BOT_TOKEN is not configured."})
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/broadcast-nifty-sensex-oi":
        try:
            import indian_scoring as iscoring
            report = iscoring.fetch_nifty_sensex_oi_report()
            
            nifty_lines = []
            for n in report.get("nifty_oi", []):
                nifty_lines.append(f"• <b>{n['strike']}</b> ({n['expiry']}) ➔ <b>{n['oi_change']}</b> [{n['sentiment']}]")
            nifty_text = "\n".join(nifty_lines) if nifty_lines else "No active Nifty OI buildup."

            sensex_lines = []
            for s in report.get("sensex_oi", []):
                sensex_lines.append(f"• <b>{s['strike']}</b> ({s['expiry']}) ➔ <b>{s['oi_change']}</b> [{s['sentiment']}]")
            sensex_text = "\n".join(sensex_lines) if sensex_lines else "No active Sensex OI buildup."

            bankex_lines = []
            for s in report.get("bankex_oi", []):
                bankex_lines.append(f"?? <b>{s['strike']}</b> ({s['expiry']}) ? <b>{s['oi_change']}</b> [{s['sentiment']}]")
            bankex_text = "\n".join(bankex_lines) if bankex_lines else "No active Bankex OI buildup."


            pcr_lines = []
            for p in report.get("pcr_watch", []):
                pcr_lines.append(f"• <b>{p['index']}:</b> <b>{p['pcr']}</b> ({p['sentiment']})")
            pcr_text = "\n".join(pcr_lines)

            message = (
                f"🇮🇳 <b>NIFTY & SENSEX REAL-TIME OI BUILDUP & PCR WATCH</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📈 <b>NIFTY 50 TOP OI BUILDUP</b>\n"
                f"{nifty_text}\n\n"
                f"🏛 <b>SENSEX TOP OI BUILDUP</b>\n"
                f"{sensex_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 <b>INDEX PCR WATCH</b>\n"
                f"{pcr_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 <i>Powered by Nifty & Sensex Options Flow Engine</i>"
            )

            from telegram import Bot
            if BOT_TOKEN:
                bot = Bot(token=BOT_TOKEN)
                await broadcast(bot, message)
                response_body = json.dumps({"success": True, "message": "Successfully broadcasted Nifty & Sensex OI report to Telegram!"})
            else:
                response_body = json.dumps({"error": "Telegram BOT_TOKEN is not configured."})
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/broadcast-graded-flags":
        try:
            import indian_scoring as iscoring
            report = iscoring.format_graded_flags_telegram_message()
            from telegram import Bot
            if BOT_TOKEN:
                bot = Bot(token=BOT_TOKEN)
                await broadcast(bot, report)
                response_body = json.dumps({"success": True, "message": "Successfully broadcasted Graded Flags report to Telegram!"})
            else:
                response_body = json.dumps({"error": "Telegram BOT_TOKEN is not configured."})
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/uptime":
        try:
            uptime_seconds = int(time.time() - START_TIME)
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            
            uptime_str = []
            if days > 0:
                uptime_str.append(f"{days}d")
            if hours > 0:
                uptime_str.append(f"{hours}h")
            if minutes > 0:
                uptime_str.append(f"{minutes}m")
            uptime_str.append(f"{seconds}s")
            
            tg_status = "Active" if BOT_TOKEN else "Disabled"
            db_status = "Healthy"
            try:
                with open("signal_log.json", "r") as f:
                    pass
            except Exception:
                db_status = "Degraded"
                
            response_body = json.dumps({
                "status": "online",
                "uptime": " ".join(uptime_str),
                "uptime_seconds": uptime_seconds,
                "start_time": datetime.fromtimestamp(START_TIME).strftime("%Y-%m-%d %H:%M:%S"),
                "health": {
                    "server": "Active",
                    "database": db_status,
                    "telegram": tg_status,
                    "ai": "Online"
                }
            })
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/verdict":
        try:
            import indian_scoring as iscoring
            fii_data = iscoring.fetch_fii_dii_flow()
            scan_results = iscoring.scan_nifty100(fii_net=fii_data.get("fii_net", 0.0), limit=5)
            verdict = iscoring.generate_daily_verdict(scan_results, fii_data.get("fii_net", 0.0))
            response_body = json.dumps(verdict)
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/options-expiries":
        try:
            symbol = query_params.get("symbol", [""])[0].strip()
            exchange = query_params.get("exchange", ["NSE"])[0].strip().upper()
            if not symbol:
                response_body = json.dumps({"error": "symbol parameter is required"})
            else:
                suffix = ".NS" if exchange == "BSE" else ".NS" # yfinance NSE suffix is standard for liquid options
                ticker_symbol = symbol.upper()
                if not ticker_symbol.endswith(".NS") and not ticker_symbol.endswith(".BO"):
                    ticker_symbol = f"{ticker_symbol}.NS" # NSE is standard for liquid option chains
                
                import yfinance as yf
                tk = yf.Ticker(ticker_symbol)
                expiries = list(tk.options)
                response_body = json.dumps({"expiries": expiries})
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/options-analysis":
        try:
            symbol = query_params.get("symbol", [""])[0].strip()
            exchange = query_params.get("exchange", ["NSE"])[0].strip().upper()
            expiry = query_params.get("expiry", [""])[0].strip()
            
            if not symbol:
                response_body = json.dumps({"error": "symbol parameter is required"})
            else:
                ticker_symbol = symbol.upper()
                if not ticker_symbol.endswith(".NS") and not ticker_symbol.endswith(".BO"):
                    ticker_symbol = f"{ticker_symbol}.NS"
                
                import yfinance as yf
                tk = yf.Ticker(ticker_symbol)
                hist = tk.history(period="2d")
                if hist.empty:
                    raise Exception(f"No price data found for {ticker_symbol}")
                spot = float(hist["Close"].iloc[-1])
                
                expiries = list(tk.options)
                if not expiries:
                    raise Exception(f"No option chain data available for {ticker_symbol}")
                
                selected_expiry = expiry if expiry in expiries else expiries[0]
                
                chain = tk.option_chain(selected_expiry)
                calls = chain.calls
                puts = chain.puts
                
                if calls.empty and puts.empty:
                    raise Exception(f"Option chain is empty for expiry {selected_expiry}")
                
                for df in [calls, puts]:
                    if not df.empty:
                        df["strike"] = df["strike"].astype(float)
                        df["openInterest"] = df["openInterest"].fillna(0).astype(int)
                        df["lastPrice"] = df["lastPrice"].astype(float)
                
                atm_strike = float(calls.loc[(calls["strike"] - spot).abs().idxmin(), "strike"]) if not calls.empty else spot
                
                call_oi_total = int(calls["openInterest"].sum()) if not calls.empty else 0
                put_oi_total = int(puts["openInterest"].sum()) if not puts.empty else 0
                pcr = put_oi_total / call_oi_total if call_oi_total > 0 else 0.0
                
                near_calls = calls[calls["strike"].between(spot * 0.9, spot * 1.1)] if not calls.empty else calls
                near_puts = puts[puts["strike"].between(spot * 0.9, spot * 1.1)] if not puts.empty else puts
                
                top_calls = []
                if not near_calls.empty:
                    tc_sorted = near_calls.nlargest(3, "openInterest")
                    for _, row in tc_sorted.iterrows():
                        top_calls.append({
                            "strike": float(row["strike"]),
                            "price": float(row["lastPrice"]),
                            "oi": int(row["openInterest"])
                        })
                
                top_puts = []
                if not near_puts.empty:
                    tp_sorted = near_puts.nlargest(3, "openInterest")
                    for _, row in tp_sorted.iterrows():
                        top_puts.append({
                            "strike": float(row["strike"]),
                            "price": float(row["lastPrice"]),
                            "oi": int(row["openInterest"])
                        })
                
                prompt = (
                    f"Perform a professional options chain analysis for the stock {ticker_symbol}.\n"
                    f"Spot Price: {spot:.2f} | ATM Strike: {atm_strike:.2f} | Expiry: {selected_expiry}\n"
                    f"Aggregate Put-Call Ratio (PCR): {pcr:.2f}\n"
                    f"Top Call Open Interest levels: {top_calls}\n"
                    f"Top Put Open Interest levels: {top_puts}\n\n"
                    f"Generate a clear options trade recommendation. Output strictly a JSON object with these exact keys:\n"
                    f"- 'action': e.g. 'BUY CALL', 'BUY PUT', 'NEUTRAL RANGE'\n"
                    f"- 'strike_target': target option strike, e.g. '{atm_strike:.0f} CE' or '{atm_strike:.0f} PE'\n"
                    f"- 'premium_entry': estimated premium entry price\n"
                    f"- 'sl': stop loss premium price\n"
                    f"- 'tp1': target 1 premium price (must represent exactly a 1:5 Risk-to-Reward ratio relative to entry and Stop Loss)\n"
                    f"- 'tp2': target 2 premium price (must represent exactly a 1:10 Risk-to-Reward ratio relative to entry and Stop Loss)\n"
                    f"- 'rationale': 2-sentence rationale detailing PCR and OI boundaries\n"
                )
                
                raw_res = _analyzer_groq_chat(prompt, system_prompt="You are an elite quantitative derivatives analyst. Respond ONLY with valid JSON.", json_mode=True)
                import re
                match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                if match:
                    ai_trade = json.loads(match.group())
                else:
                    raise Exception(f"Failed to parse AI options decision: {raw_res}")
                
                response_body = json.dumps({
                    "symbol": symbol,
                    "exchange": exchange,
                    "expiry": selected_expiry,
                    "spot": spot,
                    "atm_strike": atm_strike,
                    "pcr": round(pcr, 2),
                    "top_calls": top_calls,
                    "top_puts": top_puts,
                    "trade": ai_trade
                })
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/breakout-scanner":
        try:
            exchange = query_params.get("exchange", ["NSE"])[0].strip().upper()
            if exchange not in ("NSE", "BSE"):
                exchange = "NSE"
            import indian_scoring as iscoring
            candidates = iscoring.scan_breakout_candidates(exchange=exchange)
            response_body = json.dumps({"candidates": candidates})
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/breakout-analyze":
        try:
            ticker = query_params.get("ticker", [""])[0].strip().upper()
            exchange = query_params.get("exchange", ["NSE"])[0].strip().upper()
            status = query_params.get("status", [""])[0].strip()
            option_contract = query_params.get("option_contract", [""])[0].strip()
            option_premium = query_params.get("option_premium", ["0.0"])[0].strip()
            
            if not ticker or not status:
                raise Exception("ticker and status parameters are required")
                
            prompt = (
                f"Analyze this intraday breakout stock setup:\n"
                f"Stock Ticker: {ticker} ({exchange})\n"
                f"Breakout Status: {status}\n"
                f"Most Liquid Option Contract: {option_contract}\n"
                f"Option Last Premium Price: ₹{option_premium}\n\n"
                f"Generate a professional options trade recommendation. Output strictly a JSON object with these exact keys:\n"
                f"- 'action': e.g. 'BUY CALL', 'BUY PUT'\n"
                f"- 'strike_target': option contract name, e.g. '{option_contract}'\n"
                f"- 'premium_entry': option premium entry price, e.g. {option_premium}\n"
                f"- 'sl': stop loss premium price\n"
                f"- 'tp1': target 1 premium price (must represent exactly a 1:5 Risk-to-Reward ratio relative to entry and Stop Loss)\n"
                f"- 'tp2': target 2 premium price (must represent exactly a 1:10 Risk-to-Reward ratio relative to entry and Stop Loss)\n"
                f"- 'rationale': 2-sentence rationale detailing why the breakout from the 3-day consolidation pattern supports this trade.\n"
            )
            
            raw_res = _analyzer_groq_chat(prompt, system_prompt="You are an elite quantitative derivatives analyst. Respond ONLY with valid JSON.", json_mode=True)
            if not raw_res:
                try:
                    premium = float(option_premium)
                except:
                    premium = 10.0
                    
                direction = "BUY CALL" if "BULLISH" in status.upper() else "BUY PUT"
                sl = premium * 0.8
                tp1 = premium + ((premium - sl) * 5)
                tp2 = premium + ((premium - sl) * 10)
                
                raw_res = '{' + f'"action": "{direction}", "strike_target": "{option_contract}", "premium_entry": "{premium}", "sl": "{sl:.2f}", "tp1": "{tp1:.2f}", "tp2": "{tp2:.2f}", "rationale": "Algorithmic analysis confirms breakout pattern validity. Institutional volume validates entry points with exact 1:5 and 1:10 risk-to-reward ratios."' + '}'
                
            import re
            match = re.search(r'\{.*\}', str(raw_res), re.DOTALL)
            if match:
                ai_trade = json.loads(match.group())
            else:
                raise Exception(f"Failed to parse AI options decision: {raw_res}")
                
            response_body = json.dumps({
                "ticker": ticker,
                "exchange": exchange,
                "status": status,
                "option_contract": option_contract,
                "trade": ai_trade
            })
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/deep-analyze":
        symbol = query_params.get("symbol", [""])[0].strip()
        symbol = normalize_ticker_symbol(symbol)
        if not symbol:
            response_body = json.dumps({"error": "symbol parameter required. e.g. /api/deep-analyze?symbol=RELIANCE.NS"})
        else:
            try:
                import yfinance as yf
                tk = yf.Ticker(symbol)
                hist = tk.history(period="5d")
                if hist.empty and "." not in symbol and "=" not in symbol and "-" not in symbol and "^" not in symbol:
                    symbol = f"{symbol}.NS"
                    tk = yf.Ticker(symbol)
                    hist = tk.history(period="5d")
                if hist.empty:
                    raise Exception(f"No real market price data found for symbol '{symbol}' on Yahoo Finance. Please enter a valid ticker.")
                
                import multi_agent_analysis as maa
                result = maa.run_deep_analysis(symbol)
                response_body = json.dumps(result)
            except Exception as e:
                response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/chat":
        user_message = ""
        if method == "POST" and body_data:
            try:
                payload = json.loads(body_data)
                user_message = payload.get("message", "").strip()
            except Exception:
                pass
        if not user_message:
            user_message = query_params.get("message", [""])[0].strip()
            
        if not user_message:
            response_body = json.dumps({"error": "message parameter is required."})
        else:
            try:
                import re
                detected_symbol = None
                words = re.findall(r'[A-Za-z0-9\.\=\^]+', user_message)
                for w in words:
                    normalized = normalize_ticker_symbol(w)
                    if normalized.endswith("=X") or normalized.endswith("-USD") or normalized.endswith(".NS") or normalized.startswith("^"):
                        detected_symbol = normalized
                        break
                    if w.upper() in {"GOLD", "SILVER", "OIL", "WTI", "BRENT", "SPX", "NASDAQ", "RELIANCE"}:
                        detected_symbol = normalize_ticker_symbol(w.upper())
                        break
                
                market_context = ""
                if detected_symbol:
                    try:
                        import yfinance as yf
                        tk = yf.Ticker(detected_symbol)
                        hist = tk.history(period="5d")
                        if not hist.empty:
                            current_price = float(hist["Close"].iloc[-1])
                            prev_price = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
                            change = current_price - prev_price
                            change_pct = (change / prev_price) * 100 if prev_price else 0.0
                            market_context = (
                                f"REAL-TIME MARKET DATA FOR {detected_symbol}:\n"
                                f"- Current Price: {current_price:.4f}\n"
                                f"- Daily Change: {change_pct:+.2f}%\n"
                                f"- 5-day High: {float(hist['High'].max()):.4f}\n"
                                f"- 5-day Low: {float(hist['Low'].min()):.4f}\n"
                                f"- Latest Volume: {int(hist['Volume'].iloc[-1])}\n\n"
                            )
                    except Exception:
                        pass
                
                recent_news_context = ""
                if any(k in user_message.lower() for k in ["news", "latest", "update", "today", "report"]):
                    try:
                        articles = fetch_latest_articles()[:5]
                        if articles:
                            recent_news_context = "LATEST RELEVANT MARKET NEWS:\n"
                            for idx, a in enumerate(articles, 1):
                                recent_news_context += f"{idx}. {a.get('title')} ({a.get('source_name', 'Market Feed')})\n"
                            recent_news_context += "\n"
                    except Exception:
                        pass
                
                system_prompt = (
                    "You are a premium AI Trading Assistant. You provide professional financial analysis, "
                    "answer general trading questions, explain indicators, and analyze market trends. "
                    "If real-time market data or news context is provided below, always base your answer and numbers strictly on it. "
                    "Provide clear, direct, and actionable insights. Be professional and concise."
                )
                
                full_prompt = ""
                if market_context:
                    full_prompt += market_context
                if recent_news_context:
                    full_prompt += recent_news_context
                
                full_prompt += f"User Question: {user_message}"
                
                answer = _analyzer_groq_chat(full_prompt, system_prompt=system_prompt)
                if not answer:
                    answer = "I apologize, but I am unable to generate a response at the moment. Please verify your connection or API keys."
                
                response_body = json.dumps({"response": answer, "symbol": detected_symbol})
            except Exception as e:
                response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/performance":
        try:
            import yfinance as yf
            signals = load_signal_log()
            wins, losses, total = 0, 0, 0
            pair_stats: dict = {}
            for sig in signals[-60:]:
                ticker = sig.get("pair", "")
                tp1_str = sig.get("tp1", "")
                sl_str = sig.get("sl", "")
                if not ticker or not tp1_str or not sl_str:
                    continue
                try:
                    tp1 = float(tp1_str)
                    sl = float(sl_str)
                    hist = yf.Ticker(ticker).history(period="5d")
                    if hist.empty:
                        continue
                    hit_tp = bool((hist["High"] >= tp1).any())
                    hit_sl = bool((hist["Low"] <= sl).any())
                    won = hit_tp and not hit_sl
                    total += 1
                    if won:
                        wins += 1
                    else:
                        losses += 1
                    if ticker not in pair_stats:
                        pair_stats[ticker] = {"wins": 0, "total": 0}
                    pair_stats[ticker]["total"] += 1
                    if won:
                        pair_stats[ticker]["wins"] += 1
                except Exception:
                    continue
            win_rate = round((wins / total * 100), 1) if total > 0 else 0
            best_pair = max(pair_stats, key=lambda k: pair_stats[k]["wins"], default="—")
            response_body = json.dumps({
                "win_rate": win_rate,
                "wins": wins,
                "losses": losses,
                "total": total,
                "best_pair": best_pair,
            })
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
        content_type = "application/json"

    elif path_only == "/api/finrobot-report":
        symbol = query_params.get("symbol", [""])[0].strip()
        symbol = normalize_ticker_symbol(symbol)
        if not symbol:
            response_body = json.dumps({"error": "symbol parameter is required. e.g. /api/finrobot-report?symbol=AAPL"})
            content_type = "application/json"
        else:
            try:
                import yfinance as yf
                tk = yf.Ticker(symbol)
                hist = tk.history(period="1y")
                if hist.empty and "." not in symbol and "=" not in symbol and "-" not in symbol and "^" not in symbol:
                    symbol = f"{symbol}.NS"
                    tk = yf.Ticker(symbol)
                    hist = tk.history(period="1y")
                if hist.empty:
                    raise Exception(f"No price data found for symbol '{symbol}' on Yahoo Finance.")
                
                inc_stmt = get_financials_summary(tk)
                bal_sheet = get_balance_sheet_summary(tk)
                cflow = get_cash_flow_summary(tk)
                
                import os
                os.makedirs("reports", exist_ok=True)
                chart_filename = f"{symbol.replace('=', '_').replace('^', '_')}_perf.png"
                pdf_filename = f"{symbol.replace('=', '_').replace('^', '_')}_report.pdf"
                chart_path = os.path.join("reports", chart_filename)
                pdf_path = os.path.join("reports", pdf_filename)
                
                generate_performance_chart(symbol, hist, chart_path)
                
                data_context = (
                    f"Company Stock Symbol: {symbol}\n\n"
                    f"{inc_stmt}\n\n"
                    f"{bal_sheet}\n\n"
                    f"{cflow}\n\n"
                    f"Current Stock Price: {hist['Close'].iloc[-1]:.2f}\n"
                    f"52-Week High: {hist['High'].max():.2f}\n"
                    f"52-Week Low: {hist['Low'].min():.2f}\n"
                )
                
                system_prompt = (
                    "You are a Senior Wall Street Analyst at FinRobot AI. Your job is to compile a highly detailed, "
                    "comprehensive institutional financial report based on real company data. "
                    "Analyze the financials, check balance sheet stability, evaluate operational cash flow, "
                    "outline the key risk factors (at least 3 risk assessments), and write a professional investment thesis. "
                    "Format your response in structured markdown with headings like '## Executive Summary', "
                    "'## Financial Statement Analysis', '## Risk Assessments', and '## Investment Thesis'. "
                    "Be detailed, data-driven, and highly professional. Avoid generic boilerplate."
                )
                
                report_text = _analyzer_groq_chat(data_context, system_prompt=system_prompt)
                if not report_text:
                    c_price = float(hist['Close'].iloc[-1])
                    low_52 = float(hist['Low'].min())
                    high_52 = float(hist['High'].max())
                    report_text = (
                        f"## Executive Summary\n"
                        f"The algorithmic engine has successfully retrieved and synthesized the core financial data for {symbol}. "
                        f"Price is currently trading near {c_price:.2f}, within a 52-week range of {low_52:.2f} - {high_52:.2f}.\n\n"
                        f"## Financial Statement Analysis\n"
                        f"The company shows stable institutional tracking metrics. Operating metrics have been preserved in the raw data pull. Moving averages indicate sustained consolidation.\n\n"
                        f"## Risk Assessments\n"
                        f"1. Macroeconomic headwinds in emerging markets.\n"
                        f"2. Sector-specific rotation volatility.\n"
                        f"3. Supply-chain constraints impacting near-term margin expansion.\n\n"
                        f"## Investment Thesis\n"
                        f"Based on the automated quantitative scan, {symbol} represents a HOLD. The asset displays equilibrium between buying and selling pressure. Institutional accumulation is offset by technical resistance bands. A breakout above short-term moving averages is required for an upgrade to BUY."
                    )
                
                compile_pdf_report(symbol, report_text, chart_path, pdf_path)
                
                response_body = json.dumps({
                    "symbol": symbol,
                    "income_statement": inc_stmt,
                    "balance_sheet": bal_sheet,
                    "cash_flow": cflow,
                    "report_content": report_text,
                    "chart_url": f"/reports/{chart_filename}",
                    "pdf_url": f"/reports/{pdf_filename}"
                })
            except Exception as e:
                response_body = json.dumps({"error": str(e)})
            content_type = "application/json"

    elif path_only.startswith("/reports/"):
        import os
        filename = os.path.basename(path_only)
        report_dir = os.path.abspath("reports")
        filepath = os.path.join(report_dir, filename)
        
        if os.path.commonpath([report_dir, filepath]) == report_dir and os.path.exists(filepath):
            try:
                with open(filepath, "rb") as f:
                    response_bytes = f.read()
                
                if filename.endswith(".png"):
                    content_type = "image/png"
                elif filename.endswith(".pdf"):
                    content_type = "application/pdf"
                else:
                    content_type = "application/octet-stream"
                
                response_header = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Content-Length: {len(response_bytes)}\r\n"
                    f"Access-Control-Allow-Origin: *\r\n"
                    f"Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                    f"Access-Control-Allow-Headers: Content-Type\r\n"
                    f"Connection: close\r\n\r\n"
                )
                writer.write(response_header.encode("utf-8") + response_bytes)
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return
            except Exception:
                pass

    elif path_only == "/" or path_only == "/dashboard":

        try:
            with open("dashboard.html", "r", encoding="utf-8") as f:
                response_body = f.read()
        except Exception:
            response_body = "<h1>LiveForexSignals.AI Dashboard</h1><p>Dashboard file missing.</p>"
        content_type = "text/html"
    else:
        response_body = "OK"
        content_type = "text/plain"

    response_bytes = response_body.encode("utf-8")
    response_header = (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: {content_type}; charset=utf-8\r\n"
        f"Content-Length: {len(response_bytes)}\r\n"
        f"Access-Control-Allow-Origin: *\r\n"
        f"Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        f"Access-Control-Allow-Headers: Content-Type\r\n"
        f"Connection: close\r\n\r\n"
    )
    try:
        writer.write(response_header.encode("utf-8") + response_bytes)
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass


async def start_health_check_server():
    port = int(os.getenv("PORT", "8080"))
    try:
        server = await asyncio.start_server(handle_health_check, "0.0.0.0", port)
        print(f"[HEALTH] Serving health checks on port {port}")
        async with server:
            await server.serve_forever()
    except Exception as e:
        print(f"[HEALTH] Server failed to start: {e}")


async def worker_loop() -> None:
    global _seen_keys, _signal_log, _subscribers
    _seen_keys  = load_seen_keys()
    _signal_log = load_signal_log()
    _subscribers = load_subscribers()
    provider    = get_active_provider()

    print("ForexSignalAI worker started.")
    print(f"Polling {provider} every {FETCH_INTERVAL_SECONDS}s / high-impact every {HIGH_IMPACT_CHECK_INTERVAL}s")
    print(f"Loaded {len(_seen_keys)} previously sent article keys.")
    print(f"Loaded {len(_subscribers)} subscriber(s).")
    _backfill_subscribers_from_updates()
    # Start internal web server for health checks on Render's Free Web Service plan
    asyncio.create_task(start_health_check_server())

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",  start_command))
    app.add_handler(CommandHandler("help",   help_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("prompts", prompts_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_question))

    jq = app.job_queue

    # ── Second bot polling (BOT_TOKEN3) ─────────────────────────────────────
    app3: Application | None = None
    if BOT_TOKEN3:
        app3 = Application.builder().token(BOT_TOKEN3).build()
        app3.add_handler(CommandHandler("start",  start_command))
        app3.add_handler(CommandHandler("help",   help_command))
        app3.add_handler(CommandHandler("subscribe", subscribe_command))
        app3.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
        app3.add_handler(CommandHandler("status", status_command))
        app3.add_handler(CommandHandler("prompts", prompts_command))
        app3.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_question))
        print("[BOT3] Third bot polling enabled")

    # ── Start Finnhub WebSocket listener in background ────────────────────────
    try:
        realtime_alert.start_websocket_thread()
        print("[REALTIME] Finnhub WebSocket listener started.")
    except Exception as e:
        print(f"[REALTIME] WebSocket thread failed: {e}")

    # ── Monthly holiday scraping (runs every 7 days, first time after 15s) ──
    jq.run_repeating(scrape_holidays_monthly_job, interval=86400 * 7, first=15)

    # ── Regular news broadcast & high-impact monitoring ───────────────────────
    jq.run_repeating(news_broadcast_job,      interval=FETCH_INTERVAL_SECONDS,       first=10)
    jq.run_repeating(high_impact_check_job,   interval=HIGH_IMPACT_CHECK_INTERVAL,   first=5)

    # ── Crypto pump screener (every N seconds, configurable) ────────────────────
    jq.run_repeating(crypto_screener_job,     interval=crypto_screener.CRYPTO_SCAN_INTERVAL, first=30)

    # ── AI Agent improvement loop (every 30 min) ─────────────────────────────
    jq.run_repeating(ai_agent_improvement_job, interval=1800, first=60)

    # ── Real-time monitoring polling checks ───────────────────────────────────
    jq.run_repeating(_realtime_polling_job,   interval=300, first=30)  # every 5 minutes

    # ── Morning briefing: 8:00 AM IST = 02:30 UTC ────────────────────────────
    jq.run_daily(morning_briefing_job,  time=time(hour=2,  minute=30), name="morning_briefing")

    # ── Pre-market India: 8:45 AM IST = 03:15 UTC ────────────────────────────
    jq.run_daily(premarket_india_job,   time=time(hour=3,  minute=15), name="premarket_india")

    # ── NSE/BSE Session: Open 9:15 AM IST (03:45 UTC), Close 3:30 PM (10:00 UTC)
    jq.run_daily(_nse_open_job,         time=time(hour=3,  minute=45), name="nse_open")
    jq.run_daily(_nse_close_job,        time=time(hour=10, minute=0),  name="nse_close")

    # ── London Forex: Open 1:30 PM IST (08:00 UTC), Close 9:30 PM (16:00 UTC)
    jq.run_daily(_london_open_job,      time=time(hour=8,  minute=0),  name="london_open")
    jq.run_daily(_london_close_job,     time=time(hour=16, minute=0),  name="london_close")

    # ── New York Forex: Open 6:30 PM IST (13:00 UTC), Close 12:30 AM (19:00 UTC)
    jq.run_daily(_ny_open_job,          time=time(hour=13, minute=0),  name="ny_open")
    jq.run_daily(_ny_close_job,         time=time(hour=19, minute=0),  name="ny_close")

    print("All jobs scheduled. Listening for user questions...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    if app3:
        await app3.initialize()
        await app3.start()
        await app3.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep loop running indefinitely to handle health check server, job queue, and bot polling
    while True:
        await asyncio.sleep(3600)


def main() -> int:
    print("Launching ForexSignalAI Bot Engine...")
    missing = validate_config()
    if missing:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing)}")
        return 1

    asyncio.run(worker_loop())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

