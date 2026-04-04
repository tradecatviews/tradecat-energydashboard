import yfinance as yf
import json
from datetime import datetime
import os

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

# Load existing history safely
if os.path.exists(history_file):
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
    except:
        history = {}
else:
    history = {}

now = datetime.utcnow().isoformat()

# Append new data
for item in data:
    name = item["name"]

    if name not in history:
        history[name] = []

    # Prevent duplicates (important!)
    if len(history[name]) == 0 or history[name][-1]["price"] != item["price"]:
        history[name].append({
            "time": now,
            "price": item["price"]
        })

# Save history
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)