import requests
import time

# === CONFIGURATION ===
API_KEY = '715d277b-9f59-404d-ae75-be71e6d7baac'
DISCORD_WEBHOOK = 'https://discordapp.com/api/webhooks/1371345743885107270/Kup2etPLVwuefTaG2AQXsl1LAtXLnJS8Ck0LAeKHkdcJzJzKTaCqMH0UKvYZ_HeSS3dh'

def get_flow_data():
    url = 'https://api.unusualwhales.com/api/flow'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

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
        res = requests.post(DISCORD_WEBHOOK, json=payload)
        print("✅ Sent to Discord:", msg)
    except Exception as e:
        print("❌ Discord send failed:", e)

def filter_and_alert():
    data = get_flow_data()
    if not data or 'data' not in data:
        print("⚠️ No valid flow data returned.")
        return

    for trade in data['data']:
        if (
            trade['type'] == 'sweep' and
            trade['premium'] > 100000 and
            trade['is_otm'] and
            trade['option_type'] in ['call', 'put']
        ):
            signal = {
                "direction": trade['option_type'].upper(),
                "strike": str(trade['strike_price']),
                "expiration": trade['expiration'],
                "ticker": trade['ticker'],
                "premium": trade['premium']
            }
            send_to_discord(signal)

# Run every 5 minutes
while True:
    print("🔄 Checking for new signals...")
    filter_and_alert()
    print("⏳ Waiting 5 minutes...\n")
    time.sleep(300)
