import requests

# === CONFIGURATION ===
API_KEY = '715d277b-9f59-404d-ae75-be71e6d7baac'
TRADINGVIEW_WEBHOOK = 'https://your-ngrok-or-server-url.com/webhook'

# === FLOW FILTERS ===
def get_filtered_flow():
    url = "https://api.unusualwhales.com/api/flow"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)

    data = response.json()
    signals = []

    for trade in data.get('data', []):
        if (trade['type'] == 'sweep' and
            trade['premium'] > 100000 and
            trade['is_otm'] and
            trade['option_type'] in ['call', 'put']):

            signals.append({
                'ticker': trade['ticker'],
                'strike': trade['strike_price'],
                'expiration': trade['expiration'],
                'direction': trade['option_type'].upper()
            })

    return signals

# === SEND ALERT TO TRADINGVIEW ===
def send_alert(signal):
    payload = {
        "ticker": signal['ticker'],
        "strike": signal['strike'],
        "expiration": signal['expiration'],
        "direction": signal['direction']
    }

    res = requests.post(TRADINGVIEW_WEBHOOK, json=payload)
    print(f"Sent alert for {signal['ticker']}")

# === RUN SCRIPT ===
flow_signals = get_filtered_flow()
for signal in flow_signals:
    send_alert(signal)