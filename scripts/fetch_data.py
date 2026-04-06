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
history = {}

for name, ticker in tickers.items():
    t = yf.Ticker(ticker)
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

    history[name] = [
        {
            "time": str(idx),
            "price": round(row["Close"], 2)
        }
        for idx, row in hist.iterrows()
    ]

with open("data/energy.json", "w") as f:
    json.dump(data, f, indent=2)

with open("data/history.json", "w") as f:
    json.dump(history, f, indent=2)

print("✅ CLEAN 30-DAY DATA WRITTEN")
