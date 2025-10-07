import requests
import json
import time

API_URL = "https://gamma-api.polymarket.com/markets"
OUTPUT_FILE = "markets_data_eps.json"

# Keywords to identify earnings-related markets
KEYWORDS = ["eps", "earnings", "quarterly", "earnings per share", "q", "q1", "q2", "q3", "q4"] # can be modified based on what kind of markets are wanted


def fetch_markets(limit=1000, offset=0):
    params = {"limit": limit, "offset": offset}
    response = requests.get(API_URL, params=params)
    #error handling
    if response.status_code != 200:
        print(f" Failed to fetch markets: {response.status_code}")
        return []
    try:
        data = response.json()
    except Exception as e:
        print(f" JSON parse error: {e}")
        return []

    # Handle both list or dict structure
    if isinstance(data, list):
        markets = data
    elif isinstance(data, dict):
        markets = data.get("markets") or data.get("data") or []
    else:
        markets = []

    return markets

#filtering only eps releted markets
def is_eps_market(market):
    
    q = market.get("question", "")
    if not isinstance(q, str):
        return False
    q_lower = q.lower()
    return any(kw in q_lower for kw in KEYWORDS)

#fetching eps releted markets
def collect_eps_markets(max_pages=20, page_size=1000):
    
    found = []
    offset = 0
    for page in range(max_pages):
        print(f"Fetching page {page}, offset {offset}")
        mks = fetch_markets(limit=page_size, offset=offset)
        print(" → got", len(mks), "markets on page")

        if not mks:
            break

        for m in mks:
            if is_eps_market(m):
                found.append(m)

        offset += page_size
        time.sleep(0.2)

    print("Total EPS markets found:", len(found))
    return found

#collecting market datas
eps_markets = collect_eps_markets(max_pages=100, page_size=200)
if not eps_markets:
    print("No EPS markets found.")
else:
    print("Saving", len(eps_markets), "markets")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(eps_markets, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")