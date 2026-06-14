"""
Dashboard configuration — edit this file to change what the dashboard shows.

  1. INSTRUMENTS   -> tickers in the "Overall Market" table + charts (grouped by asset class)
  2. FRED_SERIES   -> macro indicators (inflation, unemployment, ...) — no API key
  3. YIELD_INDICES -> treasury yields via yfinance
  4. NEWS_FEEDS    -> RSS sources for the macro / Asia news strips

Adding a ticker = add one line. Adding an indicator = add one line. No other code changes needed.
"""

# ---------------------------------------------------------------------------
# 1. INSTRUMENTS  (Yahoo Finance symbols)
#    asset_class drives the filter buttons on the Overall Market tab.
# ---------------------------------------------------------------------------
INSTRUMENTS = [
    # name (display)        yahoo symbol   asset_class    region
    # ---- Indices ----
    ("S&P 500 ETF",         "SPY",         "Index",       "US"),
    ("Nasdaq 100 ETF",      "QQQ",         "Index",       "US"),
    ("Dow Jones",           "^DJI",        "Index",       "US"),
    ("Russell 2000",        "^RUT",        "Index",       "US"),
    ("Nikkei 225",          "^N225",       "Index",       "Asia"),
    ("Hang Seng",           "^HSI",        "Index",       "Asia"),
    ("FTSE 100",            "^FTSE",       "Index",       "Europe"),
    ("DAX",                 "^GDAXI",      "Index",       "Europe"),
    # ---- Equities ----
    ("Nvidia",              "NVDA",        "Equity",      "US"),
    ("Tesla",               "TSLA",        "Equity",      "US"),
    ("Apple",               "AAPL",        "Equity",      "US"),
    ("Microsoft",           "MSFT",        "Equity",      "US"),
    ("Amazon",              "AMZN",        "Equity",      "US"),
    ("Tencent (HK)",        "0700.HK",     "Equity",      "Asia"),
    ("Samsung (KR)",        "005930.KS",   "Equity",      "Asia"),
    # ---- Energy ----
    ("Brent Crude",         "BZ=F",        "Energy",      "Global"),
    ("WTI Crude",           "CL=F",        "Energy",      "Global"),
    ("Natural Gas",         "NG=F",        "Energy",      "Global"),
    # ---- Metals ----
    ("Gold",                "GC=F",        "Metals",      "Global"),
    ("Silver",              "SI=F",        "Metals",      "Global"),
    ("Copper",              "HG=F",        "Metals",      "Global"),
    # ---- Crypto ----
    ("Bitcoin",             "BTC-USD",     "Crypto",      "Global"),
    ("Ethereum",            "ETH-USD",     "Crypto",      "Global"),
    # ---- Bonds (ETFs) ----
    ("20Y+ Treasuries",     "TLT",         "Bonds",       "US"),
    ("7-10Y Treasuries",    "IEF",         "Bonds",       "US"),
    ("High-Yield Corp",     "HYG",         "Bonds",       "US"),
    ("IG Corp Bonds",       "LQD",         "Bonds",       "US"),
    # ---- FX ----
    ("US Dollar Index",     "DX-Y.NYB",    "FX",          "Global"),
    ("EUR / USD",           "EURUSD=X",    "FX",          "Global"),
    ("USD / JPY",           "USDJPY=X",    "FX",          "Global"),
    # ---- Volatility ----
    ("VIX",                 "^VIX",        "Volatility",  "US"),
]

# Order the filter buttons appear in on the Overall Market tab.
ASSET_CLASS_ORDER = ["Index", "Equity", "Energy", "Metals", "Crypto", "Bonds", "FX", "Volatility"]

# Pull 1 year of daily history so the chart's 1M/3M/6M/1Y buttons all work.
HISTORY_PERIOD   = "1y"
HISTORY_INTERVAL = "1d"

NEWS_PER_TICKER  = 6
NEWS_PER_FEED    = 8

# ---------------------------------------------------------------------------
# 2. MACRO INDICATORS — FRED public CSV (no API key needed)
#    transform: "yoy"  -> year-over-year % change (for price-index series)
#               "level"-> use the latest value as-is
# ---------------------------------------------------------------------------
FRED_SERIES = {
    "US Inflation (CPI, YoY)": ("CPIAUCSL", "yoy"),
    "Core CPI (YoY)":          ("CPILFESL", "yoy"),
    "Unemployment Rate":       ("UNRATE",   "level"),
    "Fed Funds Rate":          ("FEDFUNDS", "level"),
}

# ---------------------------------------------------------------------------
# 3. TREASURY YIELDS — via yfinance (CBOE yield indices, in %)
# ---------------------------------------------------------------------------
YIELD_INDICES = {
    "3M Treasury Yield":  "^IRX",
    "10Y Treasury Yield": "^TNX",
    "30Y Treasury Yield": "^TYX",
}

# ---------------------------------------------------------------------------
# 4. NEWS FEEDS  (plain RSS — no API keys). Failing feeds are skipped silently.
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
