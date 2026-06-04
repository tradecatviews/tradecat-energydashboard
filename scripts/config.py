"""
Dashboard configuration — edit this file to change what the dashboard shows.

Two things live here:
  1. INSTRUMENTS  -> the tickers shown in the "Overall Market" table + charts
  2. NEWS_FEEDS   -> the RSS sources for the macro / Asia news strips

Adding a ticker = add one line. Adding a news source = add one URL.
Nothing else needs to change.
"""

# ---------------------------------------------------------------------------
# 1. INSTRUMENTS  (symbol uses Yahoo Finance convention)
#    asset_class is just a label used for grouping in the UI.
# ---------------------------------------------------------------------------
INSTRUMENTS = [
    # name (display)        yahoo symbol   asset_class        region
    ("S&P 500 ETF",         "SPY",         "Equity Index",    "US"),
    ("Nasdaq 100 ETF",      "QQQ",         "Equity Index",    "US"),
    ("Nvidia",              "NVDA",        "Equity",          "US"),
    ("Tesla",               "TSLA",        "Equity",          "US"),
    ("Apple",               "AAPL",        "Equity",          "US"),
    ("Brent Crude",         "BZ=F",        "Energy",          "Global"),
    ("WTI Crude",           "CL=F",        "Energy",          "Global"),
    ("Natural Gas",         "NG=F",        "Energy",          "Global"),
    ("Gold",                "GC=F",        "Metals",          "Global"),
    ("Bitcoin",             "BTC-USD",     "Crypto",          "Global"),
    ("Ethereum",            "ETH-USD",     "Crypto",          "Global"),
    # ---- Asia ----
    ("Nikkei 225",          "^N225",       "Equity Index",    "Asia"),
    ("Hang Seng",           "^HSI",        "Equity Index",    "Asia"),
    ("Tencent (HK)",        "0700.HK",     "Equity",          "Asia"),
    ("Samsung (KR)",        "005930.KS",   "Equity",          "Asia"),
]

# How much price history to pull for the charts.
HISTORY_PERIOD   = "6mo"
HISTORY_INTERVAL = "1d"

# How many headlines to keep per ticker / per macro feed.
NEWS_PER_TICKER  = 6
NEWS_PER_FEED    = 8

# ---------------------------------------------------------------------------
# 2. NEWS FEEDS  (plain RSS — no API keys needed)
#    Any feed that fails to load is skipped silently; the rest still work.
# ---------------------------------------------------------------------------
GLOBAL_FEEDS = {
    "CNBC Markets":      "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "MarketWatch Top":   "http://feeds.marketwatch.com/marketwatch/topstories/",
    "MarketWatch Mkts":  "http://feeds.marketwatch.com/marketwatch/marketpulse/",
}

ASIA_FEEDS = {
    "CNA Business":      "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6936",
    "SCMP Business":     "https://www.scmp.com/rss/92/feed",
    "Nikkei Asia":       "https://asia.nikkei.com/rss/feed/nar",
    "Straits Times Biz": "https://www.straitstimes.com/news/business/rss.xml",
    "EconomicTimes Mkt": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Korea Times Biz":   "https://www.koreatimes.co.kr/www/rss/biz.xml",
}

# Per-ticker news comes from Yahoo Finance's per-symbol RSS (free, no key).
def yahoo_ticker_feed(symbol: str) -> str:
    return (
        "https://feeds.finance.yahoo.com/rss/2.0/headline"
        f"?s={symbol}&region=US&lang=en-US"
    )
