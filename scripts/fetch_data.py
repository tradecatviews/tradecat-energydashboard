import yfinance as yf
import json
from datetime import datetime

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

    print(hist)  # 👈 ADD THIS

    if len(hist) < 2:
        print("Not enough data, skipping")  # 👈 ADD THIS
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

with open("data/energy.json", "w") as f:
    json.dump(data, f, indent=2)

    import os

history_file = "data/history.json"

# Load existing history
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        history = json.load(f)
else:
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

# Save updated history
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)