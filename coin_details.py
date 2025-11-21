from flask import Flask, render_template, jsonify, request, url_for
import requests
import os
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)

CHART_FOLDER = "static/charts"
os.makedirs(CHART_FOLDER, exist_ok=True)

# -------------------------------
# Helper function: generate chart
# -------------------------------
def generate_chart(coin_id, coin_symbol, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    prices = data["prices"]

    x = [p[0] / 1000 for p in prices]  # timestamps
    y = [p[1] for p in prices]         # price data

    filename = f"{coin_symbol}_{days}d.png"
    filepath = os.path.join(CHART_FOLDER, filename)

    plt.figure(figsize=(8, 3))
    plt.plot(x, y)
    plt.tight_layout()
    plt.grid()
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.savefig(filepath)
    plt.close()

    return f"/static/charts/{filename}"


# ---------------------------------------------
# FULL ROUTE: Coin page + initial chart handling
# ---------------------------------------------
@app.route("/coin/<coin_id>")
def coin_page(coin_id):
    try:
        # Fetch basic coin data from CoinGecko
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()

        coin = res.json()
        coin_name = coin["name"]
        coin_symbol = coin["symbol"]
        coin_price = coin["market_data"]["current_price"]["usd"]
        coin_market_cap = coin["market_data"]["market_cap"]["usd"]
        coin_desc = coin["description"]["en"] or ""

        # Ensure default chart exists (7-day chart)
        chart_path = f"/static/charts/{coin_symbol}_7d.png"
        full_path = os.path.join(CHART_FOLDER, f"{coin_symbol}_7d.png")

        # If chart does not exist → generate once
        if not os.path.exists(full_path):
            try:
                chart_path = generate_chart(coin_id, coin_symbol, 7)
            except:
                print("Failed to generate initial chart, using placeholder")

    except Exception as e:
        return f"Error loading coin: {e}", 500

    # Render page
    return render_template(
        "coin.html",
        coin_name=coin_name,
        coin_symbol=coin_symbol,
        coin_id=coin_id,
        coin_price=coin_price,
        coin_market_cap=coin_market_cap,
        coin_desc=coin_desc,
        chart_url=chart_path
    )


# -------------------------------------------
# JSON endpoint: update chart when user clicks
# -------------------------------------------
@app.route("/coin/<coin_id>/chart")
def update_chart(coin_id):
    coin_symbol = request.args.get("symbol")
    days = request.args.get("days")

    filename = f"{coin_symbol}_{days}d.png"
    chart_url = f"/static/charts/{filename}"
    full_path = os.path.join(CHART_FOLDER, filename)

    # Try regenerating the chart
    try:
        new_chart = generate_chart(coin_id, coin_symbol, days)
        return jsonify(success=True, chart_url=new_chart)

    except Exception as e:
        print("Chart update failed:", e)
        # Return old chart instead
        return jsonify(
            success=False,
            chart_url=chart_url,
            message="Using cached chart"
        )
