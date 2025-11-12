from flask import Flask, jsonify, request, render_template
import requests
import matplotlib
matplotlib.use('Agg')  # required for servers
from matplotlib import pyplot as plt
from datetime import datetime
import os
import time

app = Flask(__name__)

#config for coin_details.py blueprint
from coin_details import coin_bp
app.register_blueprint(coin_bp)  # register the coin routes

api = "http://127.0.0.1:8000/"

def get_coins():
    return requests.get(api).json()

def charts(coins):
    os.makedirs("static/charts", exist_ok=True)
    session = requests.Session()  # reuse TCP connections

    for idx, coin in enumerate(coins, start=1):
        coin_id = coin.get("id")
        symbol = coin.get("symbol", "unknown").upper()
        success = False

        for attempt in range(3):  # retry up to 3 times
            try:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
                params = {"vs_currency": "inr", "days": 7}
                response = session.get(url, params=params, timeout=10)

                if response.status_code != 200:
                    print(f"⚠️ [{idx}] {symbol}: HTTP {response.status_code}, retrying...")
                    time.sleep(2**attempt)
                    continue

                data = response.json()
                if "prices" not in data or len(data["prices"]) == 0:
                    print(f"⚠️ [{idx}] {symbol}: no price data, skipping.")
                    break

                # sort + extract data safely
                data_sorted = sorted(data["prices"], key=lambda x: x[0])
                prices = [p[1] for p in data_sorted]
                dates = [datetime.fromtimestamp(p[0]/1000) for p in data_sorted]

                # trend color
                color = "green" if prices[0] < prices[-1] else "red"

                plt.figure(figsize=(2,1), dpi=120)
                plt.plot(dates, prices, linewidth=2, color=color)
                plt.axis("off")
                plt.tight_layout()

                save_path = f"static/charts/{symbol}.png"
                plt.savefig(save_path, transparent=True)
                plt.close()

                print(f"✅ [{idx}] Saved {symbol}")
                success = True
                break  # stop retry loop on success

            except requests.exceptions.Timeout:
                print(f"⏳ [{idx}] Timeout for {symbol}, retrying ({attempt+1}/3)...")
                time.sleep(2**attempt)
            except Exception as e:
                print(f"❌ [{idx}] Error {symbol}: {e}")
                break

        if not success:
            print(f"🚫 [{idx}] Failed to save {symbol} after 3 attempts.")

        # wait to avoid CoinGecko rate limiting
        time.sleep(1.2) 

@app.route("/")
def home():
    coins = get_coins()
    charts(coins)
    return render_template("index.html", coins=coins)

@app.route('/home')
def get_home():
    coins = get_coins()
    return render_template("home.html", coins=coins)

@app.route("/coin/<coin_id>", methods=["GET"])
def api_coins(coin_id):
    return render_template("coin_detail.html", coin_id=coin_id)


if __name__ == "__main__":
    app.run(debug=True)
