import requests
import json
import time
import csv

#getting market ids
with open("markets_data_eps.json", "r", encoding="utf-8") as f:
    markets = json.load(f)

print(f"Loaded {len(markets)} markets from markets_data.json")


#getting all trades for each market
def get_trades_for_market(market_id, limit=1000): #limit can be modified but usually site is returing max 500 trades
    
    url = "https://data-api.polymarket.com/trades"
    params = {"market": market_id, "limit": limit, "offset": 0}
    all_trades = []

    while True:
        response = requests.get(url, params=params)
        #error handling
        if response.status_code != 200:
            print(f"Failed to fetch trades for {market_id}: {response.status_code}")
            break

        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"JSON error for {market_id}")
            break

        # Handle both list and dict structures
        if isinstance(data, list):
            trades = data
        elif isinstance(data, dict):
            trades = data.get("data") or data.get("trades") or []
        else:
            trades = []

        if not trades:
            break

        all_trades.extend(trades)

        # Stop if fewer than limit trades are returned
        if len(trades) < limit:
            break

        params["offset"] += limit
        time.sleep(0.3)

    return all_trades



#creating csv file
csv_filename = "trader_data.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "market_id",
        "question",
        "active",
        "trade_id",
        "maker",
        "taker",
        "side",
        "price",
        "size",
        "timestamp"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    
    #fetching trader data and saving to csv file
    for i, m in enumerate(markets, start=1):
        market_id = m.get("market_id") or m.get("id")
        question = m.get("question", "Unknown Question")
        active = m.get("active")

        print(f"\n[{i}/{len(markets)}]  Fetching trades for: {question} (ID: {market_id})")

        if not market_id:
            print(" Skipping (missing market_id)")
            continue

        trades = get_trades_for_market(market_id)
        print(f"   → Found {len(trades)} trades")

        for t in trades:
            writer.writerow({
                "market_id": market_id,
                "question": question,
                "active": active,
                "trade_id": t.get("id"),
                "maker": t.get("maker"),
                "taker": t.get("taker"),
                "side": t.get("side"),
                "price": t.get("price"),
                "size": t.get("size"),
                "timestamp": t.get("timestamp") or t.get("created_at")
            })

        # Delay to avoid API rate limits
        time.sleep(0.5)

print(f"\n All trader data saved to {csv_filename}")