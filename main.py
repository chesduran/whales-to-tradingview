import requests
import time

API_KEY = '715d277b-9f59-404d-ae75-be71e6d7baac'
DISCORD_WEBHOOK = 'https://discordapp.com/api/webhooks/1371355612444885052/IBGwbDM4r7267UCb-IrkrXbgk1TYFWHbt1eAwcv2CugrCMJ9DJjK5g00f5vUSochQxQh'

def get_flow_data():
    url = 'https://api.unusualwhales.com/api/flow'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Text:", response.text)

    try:
        return response.json()
    except:
        return {}

def send_to_discord(signal):
    msg = f"📢 **{signal['direction']} Sweep**\n" \
          f"**Ticker:** {signal['ticker']}\n" \
          f"**Strike:** {signal['strike']}\n" \
          f"**Exp:** {signal['expiration']}\n" \
          f"**Premium:** ${signal['premium']:,}"
    payload = {"content": msg}
    requests.post(DISCORD_WEBHOOK, json=payload)

def filter_and_alert():
    data = get_flow_data()
    if not data or 'data' not in data:
        print("⚠️ No valid data.")
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

while True:
    print("🔄 Scanning...")
    filter_and_alert()
    print("⏳ Waiting 5 minutes...\n")
    time.sleep(300)
import requests
import time

API_KEY = 'YOUR_UNUSUAL_WHALES_API_KEY'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/YOUR_DISCORD_WEBHOOK'

def get_flow_data():
    url = 'https://api.unusualwhales.com/api/flow'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Text:", response.text)

    try:
        return response.json()
    except:
        return {}

def send_to_discord(signal):
    msg = f"📢 **{signal['direction']} Sweep**\n" \
          f"**Ticker:** {signal['ticker']}\n" \
          f"**Strike:** {signal['strike']}\n" \
          f"**Exp:** {signal['expiration']}\n" \
          f"**Premium:** ${signal['premium']:,}"
    payload = {"content": msg}
    requests.post(DISCORD_WEBHOOK, json=payload)

def filter_and_alert():
    data = get_flow_data()
    if not data or 'data' not in data:
        print("⚠️ No valid data.")
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

while True:
    print("🔄 Scanning...")
    filter_and_alert()
    print("⏳ Waiting 5 minutes...\n")
    time.sleep(300)
