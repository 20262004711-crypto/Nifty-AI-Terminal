from urllib.parse import urlencode, urlparse, parse_qs
import requests

AUTH_URL = "https://api.upstox.com/v2/login/authorization/dialog"
TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"

def authorization_url(client_id, redirect_uri, state="nifty-ai"):
    q = urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    })
    return AUTH_URL + "?" + q

def extract_code(value):
    value = (value or "").strip()
    if "code=" not in value:
        return value
    try:
        q = parse_qs(urlparse(value).query)
        return q.get("code", [""])[0]
    except Exception:
        return value.split("code=", 1)[1].split("&", 1)[0]

def exchange_code(code, client_id, client_secret, redirect_uri):
    r = requests.post(
        TOKEN_URL,
        data={
            "code": extract_code(code),
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=20,
    )
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"Upstox token error: {data}")
    return data
