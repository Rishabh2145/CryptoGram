from flask import Flask, jsonify
import requests

app = Flask(__name__)

BASE_URL = "https://freecryptoapi.com/api/v1"

@app.route('/api/coins')
def get_coins():
    response = requests.get(f"{BASE_URL}/coins/top?limit=20")
    return jsonify(response.json())

@app.route('/api/coin/<symbol>')
def get_coin(symbol):
    response = requests.get(f"{BASE_URL}/coins/{symbol.lower()}")
    return jsonify(response.json())

@app.route('/api/coin/<symbol>/history')
def get_coin_history(symbol):
    response = requests.get(f"{BASE_URL}/coins/{symbol.lower()}/history?interval=1d&period=30d")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
