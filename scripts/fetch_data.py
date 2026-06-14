"""
Fetch market data + news and write three JSON files the dashboard reads.

Outputs (in data/):
  market.json     -> Overall Market table (symbol, price, change%, last dividend, asset_class)
  history.json    -> price history per symbol (for the charts)
  news.json       -> { macro: {global, asia}, by_ticker: {SYM: [...]} }
  indicators.json -> macro indicators (inflation, unemployment, fed funds, yields)

Run locally:   python scripts/fetch_data.py
In CI:         the GitHub Action runs this on a schedule and commits the JSON.
"""

import csv
import io
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

import feedparser
import yfinance as yf

from config import (
    INSTRUMENTS, ASSET_CLASS_ORDER, HISTORY_PERIOD, HISTORY_INTERVAL,
    NEWS_PER_TICKER, NEWS_PER_FEED,
    FRED_SERIES, YIELD_INDICES,
    GLOBAL_FEEDS, ASIA_FEEDS, yahoo_ticker_feed,
)

NOW = datetime.now(timezone.utc).isoformat()

# write into <repo>/data regardless of where the script is run from
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def safe_round(x, n=2):
    try:
        return round(float(x), n)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# PRICES + HISTORY + LAST DIVIDEND
# ---------------------------------------------------------------------------
def fetch_prices():
    instruments, history = [], {}

    for name, symbol, asset_class, region in INSTRUMENTS:
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period=HISTORY_PERIOD, interval=HISTORY_INTERVAL)
            if hist.empty:
                print(f"  ! no price data for {symbol}, skipping")
                continue

            close = hist["Close"].dropna()
            price = safe_round(close.iloc[-1])
            prev  = close.iloc[-2] if len(close) > 1 else close.iloc[-1]
            change_pct = safe_round((close.iloc[-1] - prev) / prev * 100)

            # last dividend (— for crypto / indices / futures)
            last_div, last_div_date = None, None
            try:
                divs = t.dividends
                if divs is not None and len(divs) > 0:
                    last_div = safe_round(divs.iloc[-1])
                    last_div_date = divs.index[-1].strftime("%Y-%m-%d")
            except Exception:
                pass

            instruments.append({
                "name": name,
                "symbol": symbol,
                "asset_class": asset_class,
                "region": region,
                "price": price,
                "change_pct": change_pct,
                "last_dividend": last_div,
                "last_dividend_date": last_div_date,
            })

            # daily closes for the charts
            history[symbol] = [
                {"time": idx.strftime("%Y-%m-%d"), "price": safe_round(row)}
                for idx, row in close.items()
            ]
            print(f"  + {symbol:10s} {price}  ({change_pct:+}%)")
        except Exception as e:
            print(f"  ! {symbol} failed: {repr(e)[:120]}")

    return instruments, history


# ---------------------------------------------------------------------------
# NEWS  (RSS — per ticker + macro strips)
# ---------------------------------------------------------------------------
def parse_feed(url, limit):
    out = []
    try:
        f = feedparser.parse(url)
        for e in f.entries[:limit]:
            out.append({
                "title": e.get("title", "").strip(),
                "link": e.get("link", ""),
                "publisher": (f.feed.get("title") or "").strip(),
                "time": e.get("published", "") or e.get("updated", ""),
            })
    except Exception as e:
        print(f"  ! feed failed {url[:60]}: {repr(e)[:80]}")
    return out


def fetch_macro(feeds):
    items = []
    for label, url in feeds.items():
        got = parse_feed(url, NEWS_PER_FEED)
        for it in got:
            it["source"] = label
        items.extend(got)
        print(f"  {'+' if got else '!'} {label:18s} {len(got)} items")
    return items


def fetch_ticker_news(instruments):
    by_ticker = {}
    for inst in instruments:
        sym = inst["symbol"]
        items = parse_feed(yahoo_ticker_feed(sym), NEWS_PER_TICKER)
        if items:
            by_ticker[sym] = items
        print(f"  {'+' if items else '·'} {sym:10s} {len(items)} headlines")
        time.sleep(0.2)  # be polite to Yahoo
    return by_ticker


# ---------------------------------------------------------------------------
# MACRO INDICATORS  (FRED CSV — no key — + yfinance yields)
# ---------------------------------------------------------------------------
def fetch_fred_series(series_id):
    """Return [(YYYY-MM-DD, float), ...] from FRED's public CSV (no API key)."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    rows = []
    for r in csv.reader(io.StringIO(raw)):
        if len(r) < 2 or r[0].lower().startswith("observation") or r[0] == "DATE":
            continue
        try:
            rows.append((r[0], float(r[1])))
        except ValueError:
            continue  # "." = missing
    return rows


def fetch_indicators():
    out = []

    # FRED series (inflation, unemployment, fed funds)
    for label, (sid, transform) in FRED_SERIES.items():
        try:
            rows = fetch_fred_series(sid)
            if not rows:
                print(f"  ! {label}: no data"); continue
            date, latest = rows[-1]
            if transform == "yoy":
                if len(rows) < 13:
                    print(f"  ! {label}: not enough history for YoY"); continue
                year_ago = rows[-13][1]
                value = safe_round((latest / year_ago - 1) * 100)
            else:
                value = safe_round(latest)
            out.append({"name": label, "value": value, "unit": "%",
                        "asof": date[:7], "source": "FRED"})
            print(f"  + {label:26s} {value}%  (as of {date[:7]})")
        except Exception as e:
            print(f"  ! {label} failed: {repr(e)[:90]}")

    # Treasury yields via yfinance
    for label, sym in YIELD_INDICES.items():
        try:
            h = yf.Ticker(sym).history(period="5d")["Close"].dropna()
            if h.empty:
                print(f"  ! {label}: no data"); continue
            value = safe_round(h.iloc[-1])
            out.append({"name": label, "value": value, "unit": "%",
                        "asof": h.index[-1].strftime("%Y-%m-%d"), "source": "CBOE"})
            print(f"  + {label:26s} {value}%")
        except Exception as e:
            print(f"  ! {label} failed: {repr(e)[:90]}")

    # Yield-curve spread (10Y - 3M): a watched recession signal
    by = {i["name"]: i["value"] for i in out}
    if "10Y Treasury Yield" in by and "3M Treasury Yield" in by:
        spread = safe_round(by["10Y Treasury Yield"] - by["3M Treasury Yield"])
        out.append({"name": "Yield Curve (10Y-3M)", "value": spread, "unit": "pp",
                    "asof": NOW[:10], "source": "derived"})
        print(f"  + {'Yield Curve (10Y-3M)':26s} {spread}pp")

    return out


# ---------------------------------------------------------------------------
def main():
    print("== prices ==")
    instruments, history = fetch_prices()

    print("== global macro news ==")
    global_news = fetch_macro(GLOBAL_FEEDS)
    print("== asia macro news ==")
    asia_news = fetch_macro(ASIA_FEEDS)
    print("== per-ticker news ==")
    by_ticker = fetch_ticker_news(instruments)
    print("== macro indicators ==")
    indicators = fetch_indicators()

    market = {"updated": NOW, "asset_class_order": ASSET_CLASS_ORDER,
              "instruments": instruments}
    news = {
        "updated": NOW,
        "macro": {"global": global_news, "asia": asia_news},
        "by_ticker": by_ticker,
    }
    indicators_doc = {"updated": NOW, "indicators": indicators}

    with open(os.path.join(DATA_DIR, "market.json"), "w") as f:
        json.dump(market, f, indent=2)
    with open(os.path.join(DATA_DIR, "history.json"), "w") as f:
        json.dump(history, f, indent=2)
    with open(os.path.join(DATA_DIR, "news.json"), "w") as f:
        json.dump(news, f, indent=2)
    with open(os.path.join(DATA_DIR, "indicators.json"), "w") as f:
        json.dump(indicators_doc, f, indent=2)

    print(f"\n✅ wrote {len(instruments)} instruments, "
          f"{len(global_news)+len(asia_news)} macro items, "
          f"{len(by_ticker)} tickers with news, "
          f"{len(indicators)} indicators")


if __name__ == "__main__":
    main()
