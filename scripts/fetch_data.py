"""
Fetch market data + news and write three JSON files the dashboard reads.

Outputs (in data/):
  market.json   -> Overall Market table  (symbol, price, change%, last dividend)
  history.json  -> price history per symbol (for the charts)
  news.json     -> { macro: {global, asia}, by_ticker: {SYM: [...]} }

Run locally:   python scripts/fetch_data.py
In CI:         the GitHub Action runs this on a schedule and commits the JSON.
"""

import json
import os
import time
from datetime import datetime, timezone

import feedparser
import yfinance as yf

from config import (
    INSTRUMENTS, HISTORY_PERIOD, HISTORY_INTERVAL,
    NEWS_PER_TICKER, NEWS_PER_FEED,
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
def main():
    print("== prices ==")
    instruments, history = fetch_prices()

    print("== global macro news ==")
    global_news = fetch_macro(GLOBAL_FEEDS)
    print("== asia macro news ==")
    asia_news = fetch_macro(ASIA_FEEDS)
    print("== per-ticker news ==")
    by_ticker = fetch_ticker_news(instruments)

    market = {"updated": NOW, "instruments": instruments}
    news = {
        "updated": NOW,
        "macro": {"global": global_news, "asia": asia_news},
        "by_ticker": by_ticker,
    }

    with open(os.path.join(DATA_DIR, "market.json"), "w") as f:
        json.dump(market, f, indent=2)
    with open(os.path.join(DATA_DIR, "history.json"), "w") as f:
        json.dump(history, f, indent=2)
    with open(os.path.join(DATA_DIR, "news.json"), "w") as f:
        json.dump(news, f, indent=2)

    print(f"\n✅ wrote {len(instruments)} instruments, "
          f"{len(global_news)+len(asia_news)} macro items, "
          f"{len(by_ticker)} tickers with news")


if __name__ == "__main__":
    main()
