import yfinance as yf
import json
from datetime import datetime
import os
import requests

tickers = {
    "Brent": "BZ=F",
    "WTI": "CL=F",
    "GasoilProxy": "HO=F",
    "NatGas": "NG=F"
}

data = []

for name, ticker in tickers.items():
    print(f"Fetching {name} ({ticker})")

    t = yf.Ticker(ticker)
    hist = t.history(period="5d")

    if hist.empty or len(hist) < 2:
        print(f"Not enough data for {name}, skipping")
        continue

    latest = hist.iloc[-1]
    prev = hist.iloc[-2]

    price = round(latest["Close"], 2)
    change_pct = round(((price - prev["Close"]) / prev["Close"]) * 100, 2)

    data.append({
        "name": name,
        "price": price,
        "change_pct": change_pct,
        "timestamp": datetime.utcnow().isoformat()
    })

# Save latest snapshot
with open("data/energy.json", "w") as f:
    json.dump(data, f, indent=2)

# --- HISTORY LOGIC ---

history_file = "data/history.json"

url = "https://raw.githubusercontent.com/tradecatviews/tradecat-energydashboard/main/data/history.json"

try:
    response = requests.get(url)
    history = response.json()
except:
    history = {}

now = datetime.utcnow().isoformat()

for item in data:
    name = item["name"]

    if name not in history:
        history[name] = []

    history[name].append({
        "time": now,
        "price": item["price"]
    })

with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

# Save history
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

print("HISTORY LENGTHS:", {k: len(v) for k, v in history.items()})