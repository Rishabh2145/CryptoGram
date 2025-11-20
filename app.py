from flask import Flask, jsonify, request, render_template
import requests
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime
import os
import time

app = Flask(__name__)

# ─────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────
CHART_FOLDER = "static/charts"
os.makedirs(CHART_FOLDER, exist_ok=True)

COIN_API = "https://api.coingecko.com/api/v3/coins"
LOCAL_API = "http://127.0.0.1:8000/"   # your local API

# ─────────────────────────────────────────────
# UTILITY: Get all coins from your local API
# ─────────────────────────────────────────────
def get_coins():
    return requests.get(LOCAL_API).json()

# ─────────────────────────────────────────────
# UTILITY: Generate a 7-day small icon chart
# ─────────────────────────────────────────────
def charts(coins):
    os.makedirs("static/charts", exist_ok=True)
    session = requests.Session()

    for idx, coin in enumerate(coins, start=1):
        coin_id = coin.get("id")
        symbol = coin.get("symbol", "unknown").upper()
        save_path = f"static/charts/{symbol}.png"

        # Skip generation if file already exists
        if os.path.exists(save_path):
            continue

        for attempt in range(3):
            try:
                url = f"{COIN_API}/{coin_id}/market_chart"
                params = {"vs_currency": "inr", "days": 7}
                response = session.get(url, params=params, timeout=10)

                if response.status_code != 200:
                    time.sleep(2**attempt)
                    continue

                data = response.json()
                prices = data.get("prices", [])
                if not prices:
                    break

                prices_sorted = sorted(prices, key=lambda x: x[0])
                y = [p[1] for p in prices_sorted]
                x = [datetime.fromtimestamp(p[0]/1000) for p in prices_sorted]

                color = "green" if y[0] < y[-1] else "red"

                plt.figure(figsize=(2, 1), dpi=120)
                plt.plot(x, y, color=color, linewidth=2)
                plt.axis("off")
                plt.tight_layout()
                plt.savefig(save_path, transparent=True)
                plt.close()

                break

            except:
                time.sleep(2**attempt)

        time.sleep(1.1)  # avoid CoinGecko rate limits

# ─────────────────────────────────────────────
# NEW: Generate full-size chart for coin pages
# ─────────────────────────────────────────────
def generate_chart(coin_id, symbol, days):
    url = f"{COIN_API}/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    prices = data["prices"]

    x = [p[0] / 1000 for p in prices]
    y = [p[1] for p in prices]

    filename = f"{symbol}_{days}d.png"
    filepath = os.path.join(CHART_FOLDER, filename)

    plt.figure(figsize=(8, 3))
    plt.plot(x, y)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return f"/static/charts/{filename}"

# ─────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────
@app.route("/")
def home():
    coins = get_coins()
    charts(coins)
    return render_template("index.html", coins=coins)

@app.route("/home")
def get_home():
    coins = get_coins()
    return render_template("home.html", coins=coins)

# ─────────────────────────────────────────────
# NEW: FULL COIN DETAIL PAGE
# ─────────────────────────────────────────────
@app.route("/coin/<coin_id>")
def coin_page(coin_id):
    url = f"{COIN_API}/{coin_id}"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        coin = res.json()

        coin_name = coin["name"]
        coin_symbol = coin["symbol"]
        coin_price = coin["market_data"]["current_price"]["usd"]
        coin_market_cap = coin["market_data"]["market_cap"]["usd"]
        coin_desc = coin["description"]["en"] or ""

        # Ensure default chart exists
        default_chart = f"static/charts/{coin_symbol}_7d.png"
        if not os.path.exists(default_chart):
            try:
                generate_chart(coin_id, coin_symbol, 7)
            except:
                print("❌ Failed to generate default coin chart")

    except Exception as e:
        return f"Error loading coin: {e}", 500

    return render_template(
        "coin_detail.html",
        coin_id=coin_id,
        coin_name=coin_name,
        coin_symbol=coin_symbol,
        coin_price=coin_price,
        coin_market_cap=coin_market_cap,
        coin_desc=coin_desc,
        chart_url=f"/static/charts/{coin_symbol}_7d.png"
    )

# ─────────────────────────────────────────────
# JSON ENDPOINT: Update chart on click
# ─────────────────────────────────────────────
@app.route("/coin/<coin_id>/chart")
def update_chart(coin_id):
    symbol = request.args.get("symbol")
    days = request.args.get("days")

    filename = f"{symbol}_{days}d.png"
    existing_path = f"/static/charts/{filename}"

    try:
        new_chart = generate_chart(coin_id, symbol, days)
        return jsonify(success=True, chart_url=new_chart)

    except Exception as e:
        print("Chart update failed:", e)
        # Return old chart
        return jsonify(
            success=False,
            chart_url=existing_path,
            message="Using cached chart"
        )

# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
