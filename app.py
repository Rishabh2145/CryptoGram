from flask import Flask, jsonify, request, render_template
import requests
import pandas as pd
from matplotlib import pyplot as plt

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)