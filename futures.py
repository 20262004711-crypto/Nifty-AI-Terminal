import gzip, json, time
from pathlib import Path
import requests

URL = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"
CACHE = Path("futures_key_cache.json")

def get_nifty_futures_key():
    month = time.strftime("%Y-%m")
    if CACHE.exists():
        try:
            c = json.loads(CACHE.read_text())
            if c.get("month") == month and c.get("key"):
                return c["key"]
        except Exception:
            pass

    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    data = json.loads(gzip.decompress(r.content))

    futs = [
        d for d in data
        if str(d.get("instrument_type", "")).upper() == "FUT"
        and str(d.get("name", "")).upper() == "NIFTY"
        and d.get("exchange") in ("NSE_FO", "NFO")
    ]
    if not futs:
        futs = [
            d for d in data
            if "FUT" in str(d.get("instrument_type", "")).upper()
            and str(d.get("trading_symbol", "")).upper().startswith("NIFTY")
            and "BANK" not in str(d.get("trading_symbol", "")).upper()
            and "FIN" not in str(d.get("trading_symbol", "")).upper()
        ]
    if not futs:
        raise RuntimeError("NIFTY futures instrument nahi mila.")

    futs.sort(key=lambda d: d.get("expiry", 0))
    key = futs[0]["instrument_key"]
    CACHE.write_text(json.dumps({"month": month, "key": key}, indent=2))
    return key
