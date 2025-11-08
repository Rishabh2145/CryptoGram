from flask import Flask, jsonify, request
import requests
import pandas as pd
from matplotlib import pyplot as plt

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the Flask API!"


if __name__ == "__main__":
    app.run(debug=True)