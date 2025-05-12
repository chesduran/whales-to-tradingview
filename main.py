import requests
import time

API_KEY = 715d277b-9f59-404d-ae75-be71e6d7baac
TRADINGVIEW_WEBHOOK = 'https://your-tradingview-webhook.com'  # Replace with your real TradingView webhook

def get_flow_data():
    url = 'https://api.unusualwhales.com/api/flow'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    return response.json()

def send_to_tradingview(signal):
    payload = {
        "dir": signal["direction"],
        "strike": signal["strike"],
        "exp": signal["expiration"]
    }
    requests.post(TRADINGVIEW_WEBHOOK, json=payload)

def filter_and_alert():
    flow = get_flow_data()
    for trade in flow.get("data", []):
        if (trade['type'] == 'sweep' and
            trade['premium'] > 100000 and
            trade['is_otm'] and
            trade['option_type'] in ['call', 'put']):

            signal = {
                "direction": trade['option_type'].upper(),
                "strike": str(trade['strike_price']),
                "expiration": trade['expiration']
            }
            print("Sending alert:", signal)
            send_to_tradingview(signal)

# Run this in a loop every 5 minutes
while True:
    filter_and_alert()
    time.sleep(300)