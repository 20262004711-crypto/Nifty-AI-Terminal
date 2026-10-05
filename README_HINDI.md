# NIFTY AI Scanner - Android Project

## Is version mein kya bana hai

Ye project aapke existing:
- `nifty_option_engine.py`
- `upstox_adapter.py`

ko change kiye bina mobile Kivy UI ke saath use karta hai.

App flow:
1. User apna Upstox API Key, Secret aur registered Redirect URI deta hai.
2. "Open Upstox Login" se Upstox login hota hai.
3. Redirect URL/code app mein paste karke access token milta hai.
4. App current NIFTY futures key automatically dhoondti/cache karti hai.
5. 5-minute NIFTY snapshot lekar existing DecisionEngine run hota hai.
6. Mobile screen par Status, Trend, Spot, AI Score, Support/Resistance, Entry, SL aur Targets dikhte hain.

## Important

Ye **APK source project / Phase-1 build** hai. Is chat environment mein Android SDK/Buildozer se final signed APK compile nahi ki gayi hai.

Pydroid 3 mein normal `.py` run ho sakta hai, lekin APK build ke liye Buildozer/Linux toolchain chahiye.

## Public distribution ke liye

Upstox ki official OAuth documentation ke mutabik authorization-code exchange mein
`client_secret` confidential rehna chahiye aur token exchange server-to-server hota hai.
Isliye agar ye APK bahut saare users ko deni hai, final production version mein
client secret ko APK ke andar hard-code nahi karna chahiye.

Is project ka current UI OAuth flow ko test/validate karne ke liye hai. Next production
phase mein OAuth callback + secure backend/token service add ki ja sakti hai.

## Build (Linux/Termux/Buildozer environment)

```bash
pip install buildozer cython
buildozer android debug
```

First build mein Android dependencies download hone ki wajah se kaafi time lag sakta hai.

APK normally `bin/` folder mein generate hogi.

## Files

- `main.py` - Android/Kivy UI
- `nifty_option_engine.py` - original decision engine
- `upstox_adapter.py` - original Upstox data adapter
- `upstox_auth.py` - OAuth helper
- `futures.py` - automatic NIFTY futures-key discovery
- `buildozer.spec` - Android build configuration
- `dashboard.html` - existing browser dashboard
- `dashboard_data.json` - existing dashboard data snapshot

`.pyc` files ko intentionally include nahi kiya gaya hai; original `.py` source modules use ho rahe hain.
