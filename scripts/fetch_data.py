import yfinance as yf
import json
from datetime import datetime
import requests
import os

tickers = {
    "Brent": "BZ=F",
    "WTI": "CL=F",
    "GasoilProxy": "HO=F",
    "NatGas": "NG=F"
}

# --- STEP 1: FETCH DATA ---

data = []

for name, ticker in tickers.items():
    t = yf.Ticker(ticker)

    # Get 30 days of daily data
    hist = t.history(period="30d")

    if hist.empty:
        continue

    latest = hist.iloc[-1]
    prev = hist.iloc[-2] if len(hist) > 1 else latest

    price = round(latest["Close"], 2)
    change_pct = round(((price - prev["Close"]) / prev["Close"]) * 100, 2)

    data.append({
        "name": name,
        "price": price,
        "change_pct": change_pct,
        "timestamp": datetime.utcnow().isoformat()
    })

# Save snapshot
with open("data/energy.json", "w") as f:
    json.dump(data, f, indent=2)

# --- STEP 2: LOAD EXISTING HISTORY FROM GITHUB ---

url = "https://raw.githubusercontent.com/tradecatviews/tradecat-energydashboard/main/data/history.json"

try:
    response = requests.get(url)
    history = response.json()
except:
    history = {}

# --- STEP 3: BUILD / UPDATE HISTORY ---

for name, ticker in tickers.items():
    t = yf.Ticker(ticker)
    hist = t.history(period="30d")

    if hist.empty:
        continue

    # Convert dataframe → list of points
    new_points = [
        {
            "time": str(idx),
            "price": round(row["Close"], 2)
        }
        for idx, row in hist.iterrows()
    ]

# FORCE overwrite history (temporary)
        # 🔥 FIRST RUN → seed full 30 days
        history[name] = new_points
    else:
        # Append only latest point
        last_price = history[name][-1]["price"]

        latest_price = new_points[-1]["price"]

        if latest_price != last_price:
            history[name].append(new_points[-1])

# --- STEP 4: SAVE HISTORY ---

with open("data/history.json", "w") as f:
    json.dump(history, f, indent=2)

print("✅ Data + 30-day history updated")