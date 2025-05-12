import requests
import time
from datetime import datetime, timedelta  # ✅ Fixes the error you had

# === CONFIGURATION ===
API_KEY = '715d277b-9f59-404d-ae75-be71e6d7baac'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1371367462750392340/9OhaBo_rrmWzs3HDhEy-1DrgmBu05WO3vOnfJFy62oCgvD52HsOE1grwvU6m4WegTSyd'

# === FILTERS ===
MIN_PREMIUM = 50
MAX_PREMIUM = 300
MAX_EXPIRY_DAYS = 30
MIN_VOLUME = 500
MIN_SIZE = 10
TICKERS_TO_INCLUDE = []  # e.g. ['SPY', 'QQQ'] or leave empty for all

def get_flow_data():
    url = 'https://api.unusualwhales.com/api/option-trades/flow-alerts'
    headers = {
        'Authorization': f'Bearer ' + API_KEY,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Preview:", response.text[:200])
    try:
        return response.json()
    except Exception as e:
        print("❌ JSON decode error:", e)
        return {}

def send_to_discord(signal):
    msg = f"📢 **{signal['direction']} Sweep Alert**\n" \
          f"**{signal['ticker']}** | Strike: {signal['strike']} | Exp: {signal['expiration']}\n" \
          f"Premium: ${signal['premium']} | Spot: ${signal['spot']} | Δ: {signal['delta']} | Size: {signal['size']} | Vol: {signal['volume']}"
    payload = {"content": msg}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print("✅ Sent to Discord:", msg)
    except Exception as e:
        print("❌ Discord error:", e)

def filter_and_alert():
    data = get_flow_data()
    if not data or 'data' not in data:
        print("⚠️ No valid data.")
        return

    for trade in data['data'][:25]:
        try:
            # Required fields
            ticker = trade['ticker'].upper()
            option_type = trade['type'].lower()
            strike = float(trade['strike'])
            expiry = trade['expiry']
            spot = float(trade['underlying_price'])
            delta = float(trade['greeks']['delta']) if trade.get('greeks') else None
            ask = float(trade['ask'])
            premium = ask * 100
            volume = int(trade['volume'])
            size = int(trade['size'])
            has_sweep = trade.get('has_sweep', False)

            # Basic checks
            if not expiry or not delta:
                continue
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
            days_to_expiry = (expiry_date - datetime.now()).days
            if days_to_expiry < 0 or days_to_expiry > MAX_EXPIRY_DAYS:
                continue

            if premium < MIN_PREMIUM or premium > MAX_PREMIUM:
                continue
            if volume < MIN_VOLUME or size <= MIN_SIZE:
                continue
            if TICKERS_TO_INCLUDE and ticker not in TICKERS_TO_INCLUDE:
                continue
            if not has_sweep:
                continue

            # Directional delta check
            if option_type == 'call' and delta < 0.3:
                continue
            if option_type == 'put' and delta > -0.3:
                continue

            # Avoid ITM contracts
            if option_type == 'call' and strike < spot:
                continue
            if option_type == 'put' and strike > spot:
                continue

            # Passed all filters
            signal = {
                "direction": option_type.upper(),
                "strike": strike,
                "expiration": expiry,
                "ticker": ticker,
                "premium": round(premium, 2),
                "spot": round(spot, 2),
                "delta": round(delta, 2),
                "volume": volume,
                "size": size
            }
            send_to_discord(signal)

        except Exception as e:
            print(f"⚠️ Error parsing trade: {e}")

# === LOOP ===
while True:
    print("🔄 Checking for flow...")
    filter_and_alert()
    print("⏳ Waiting 5 minutes...\n")
    time.sleep(300)
