from flask import Blueprint, render_template, request
import requests
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime
import os

coin_bp = Blueprint("coin_bp", __name__)

# Ensure charts directory exists
os.makedirs("static/charts", exist_ok=True)

@coin_bp.route("/coin/<coin_id>", methods=["GET"])
def coin_detail(coin_id):
    """
    Render coin detail page with description, price, market cap, and default 7-day chart
    """
    # Fetch coin data from CoinGecko
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return f"Error fetching data for {coin_id}", 500

    coin = response.json()
    coin_name = coin.get("name", coin_id)
    coin_symbol = coin.get("symbol", "unknown").upper()
    coin_desc = coin.get("description", {}).get("en", "No description available.")[:600]

    market_data = coin.get("market_data", {})
    coin_price = market_data.get("current_price", {}).get("usd", 0)
    coin_market_cap = market_data.get("market_cap", {}).get("usd", 0)

    # Generate 7-day chart
    try:
        chart_url = generate_chart(coin_id, coin_symbol, days=7)
    except Exception as e:
        print(f"Error generating chart: {e}")
        chart_url = None

    return render_template(
        "coin_detail.html",
        coin_id=coin_id,
        coin_name=coin_name,
        coin_symbol=coin_symbol,
        coin_desc=coin_desc,
        coin_price=coin_price,
        coin_market_cap=coin_market_cap,
        chart_url=chart_url
    )


def generate_chart(coin_id, symbol, days=7):
    """
    Generate and save a chart for the coin for 'days' days.
    Returns the relative path to the saved image.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "prices" not in data or len(data["prices"]) == 0:
        raise ValueError("No price data")

    prices = [p[1] for p in data["prices"]]
    dates = [datetime.fromtimestamp(p[0]/1000) for p in data["prices"]]

    color = "green" if prices[0] < prices[-1] else "red"

    plt.figure(figsize=(6, 3))
    plt.plot(dates, prices, color=color, linewidth=2)
    plt.title(f"{symbol} - Last {days} Days")
    plt.xticks(rotation=30, fontsize=8)
    plt.tight_layout()

    save_path = f"static/charts/{symbol}_{days}d.png"
    plt.savefig(save_path, transparent=True)
    plt.close()

    return f"/{save_path}"
