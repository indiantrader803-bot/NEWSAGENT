import os
import requests

def get_groww_price(trading_symbol, segment="CASH", exchange="NSE"):
    """
    Fetch real-time price from Groww API.
    segment: 'CASH' for stocks/indices, 'FNO' for options.
    """
    token = os.getenv("GROWW_ACCESS_TOKEN")
    if not token:
        return None
        
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "X-API-VERSION": "1.0"
    }
    
    url = f"https://api.groww.in/v1/live-data/quote?exchange={exchange}&segment={segment}&trading_symbol={trading_symbol}"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                return data.get("payload", {}).get("last_price")
    except Exception as e:
        pass
    
    return None
