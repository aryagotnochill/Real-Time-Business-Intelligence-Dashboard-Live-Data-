import os
import requests
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

ALPHA_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
try:
    import yfinance as yf
except Exception:
    yf = None

def get_stock_quote(symbol="AAPL"):
    if not ALPHA_KEY:
        return {"error": "Missing ALPHAVANTAGE_API_KEY"}
    url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get("Global Quote", {})
        price = float(data.get("05. price", 0)) if data else 0
        change = float(data.get("09. change", 0)) if data else 0
        return {"symbol": symbol, "price": price, "change": change, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"error": str(e)}


def get_stock_yfinance(symbol="AAPL"):
    """Fetch latest price using yfinance (no API key required)."""
    if yf is None:
        return {"error": "yfinance not installed"}
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d", interval="1m")
        if hist is None or hist.empty:
            return {"error": "no data"}
        # use last two close values to compute change
        closes = hist['Close'].dropna()
        if len(closes) == 0:
            return {"error": "no close data"}
        latest = float(closes.iloc[-1])
        prev = float(closes.iloc[-2]) if len(closes) > 1 else latest
        change = round(latest - prev, 4)
        return {"symbol": symbol, "price": latest, "change": change, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"error": str(e)}


def get_stock_history(symbol="AAPL", period="7d", interval="1h"):
    """Return historical price series using yfinance as dict with timestamps and close prices."""
    if yf is None:
        return {"error": "yfinance not installed"}
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period=period, interval=interval)
        if hist is None or hist.empty:
            return {"error": "no data"}
        closes = hist['Close'].dropna()
        timestamps = [idx.isoformat() for idx in closes.index]
        prices = [float(v) for v in closes.values]
        return {"symbol": symbol, "timestamps": timestamps, "prices": prices}
    except Exception as e:
        return {"error": str(e)}

def get_crypto_price(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        price = r.json().get(coin_id, {}).get("usd")
        return {"coin": coin_id, "price": price, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"error": str(e)}

def get_twitter_metrics(username="twitter"):
    token = os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        return {"error": "Missing TWITTER_BEARER_TOKEN"}
    headers = {"Authorization": f"Bearer {token}"}
    try:
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        user = r.json().get("data", {})
        user_id = user.get("id")
        return {"username": username, "id": user_id, "note": "Add further endpoints for tweets/engagement"}
    except Exception as e:
        return {"error": str(e)}

def push_to_powerbi(payload, push_url=None):
    if not push_url:
        push_url = os.getenv("POWERBI_PUSH_URL")
    if not push_url:
        return {"error": "Missing POWERBI_PUSH_URL"}
    try:
        r = requests.post(push_url, json=payload, timeout=10)
        r.raise_for_status()
        return {"status": "ok", "code": r.status_code}
    except Exception as e:
        return {"error": str(e)}
