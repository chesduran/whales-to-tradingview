import requests
import time

# === CONFIGURATION ===
API_KEY = '715d277b-9f59-404d-ae75-be71e6d7baac'  # <-- Replace with your API key
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1371367462750392340/9OhaBo_rrmWzs3HDhEy-1DrgmBu05WO3vOnfJFy62oCgvD52HsOE1grwvU6m4WegTSyd'  # <-- Replace with your webhook

# === FILTERS ===
MIN_PREMIUM = 250             # Minimum estimated premium in dollars
MAX_EXPIRY_DAYS = 30          # Only options expiring within 30 days
TICKERS_TO_INCLUDE = []       # Add tickers like ['SPY', 'QQQ'], or leave empty for all

def get_flow_data():
    url = 'https://api.unusualwhales.com/api/option-trades/flow-alerts'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
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
          f"**Ticker:** {signal['ticker']}\n" \
          f"**Strike:** {signal['strike']}\n" \
          f"**Exp:** {signal['expiration']}\n" \
          f"**Premium:** ${signal['premium']:,}"
    payload = {"content": msg}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print("✅ Sent to Discord:", msg)
    except Exception as e:
        print("❌ Failed to send to Discord:", e)

def filter_and_alert():
    data = get_flow_data()
    if not data or 'data' not in data:
        print("⚠️ No valid flow data returned.")
        return

    for trade in data['data'][:20]:
        try:
            ticker = trade['ticker'].upper()
            premium_estimate = float(trade['ask']) * 100
            expiry_str = trade['expiry']
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
            days_to_expiry = (expiry_date - datetime.now()).days

            # === FILTERS ===
            if days_to_expiry > MAX_EXPIRY_DAYS or days_to_expiry < 0:
                continue
            if premium_estimate < MIN_PREMIUM:
                continue
            if TICKERS_TO_INCLUDE and ticker not in TICKERS_TO_INCLUDE:
                continue
            if not trade.get('has_sweep', False):
                continue  # Skip if not a sweep
            if not trade.get('is_otm', False):
                continue  # Skip if not out-of-the-money

            # === SEND SIGNAL ===
            signal = {
                "direction": trade['type'].upper(),
                "strike": str(trade['strike']),
                "expiration": expiry_str,
                "ticker": ticker,
                "premium": premium_estimate
            }
            send_to_discord(signal)

        except KeyError as e:
            print(f"⚠️ Missing key: {e}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

# === LOOP ===
while True:
    print("🔄 Checking for new signals...")
    filter_and_alert()
    print("⏳ Waiting 5 minutes...\n")
    time.sleep(300)
