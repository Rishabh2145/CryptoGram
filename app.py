from flask import Flask, jsonify, request, render_template
import requests
import matplotlib
matplotlib.use('Agg')  # required for servers
from matplotlib import pyplot as plt
from datetime import datetime
import os
import time

app = Flask(__name__)

api = "http://127.0.0.1:8000/"

def get_coins():
    return requests.get(api).json()

def charts(coins):
    os.makedirs("static/charts", exist_ok=True)

    for coin in coins:
        coin_id = coin.get('id')
        symbol = coin.get('symbol', 'unknown').upper()
        retries = 3 

        for attempt in range(retries):
            try:
                chart_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
                params = {"vs_currency": "inr", "days": 365}
                response = requests.get(chart_url, params=params)

                # Retry on non-200 responses
                if response.status_code != 200:
                    print(f"⚠️ {symbol}: status {response.status_code}, retrying...")
                    time.sleep(2)
                    continue

                data = response.json()

                # Check if valid data present
                if "prices" not in data or len(data["prices"]) == 0:
                    print(f"⚠️ {symbol}: no price data found, skipping.")
                    break

                prices = [p[1] for p in data["prices"]]
                dates = [datetime.fromtimestamp(p[0]/1000) for p in data["prices"]]


                color = "green" if prices[0] < prices[-1] else "red"

                plt.figure(figsize=(2, 1))
                plt.plot(dates, prices, linewidth=2, color=color)
                plt.axis("off")
                plt.tight_layout()

                path = f"static/charts/{symbol}.png"
                plt.savefig(path, bbox_inches='tight', pad_inches=0, transparent=True)
                plt.close()
                print(f"✅ Saved {symbol}")
                time.sleep(1.2)  # avoid hitting rate limits
                break  # success — exit retry loop

            except requests.exceptions.Timeout:
                print(f"⏳ Timeout for {symbol}, retrying ({attempt+1}/{retries})...")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Error for {symbol}: {e}")
                break  

@app.route("/")
def home():
    coins = get_coins()
    charts(coins)
    return render_template("index.html", coins=coins)

@app.route('/home')
def get_home():
    coins = get_coins()
    return render_template("home.html", coins=coins)

if __name__ == "__main__":
    app.run(debug=True)
