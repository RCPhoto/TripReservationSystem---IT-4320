import os
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import requests
from datetime import datetime

app = Flask(__name__)

def MakeDataframe(file):
    dataframe = pd.read_sql_table(file)
    return dataframe

def 

@app.route("/", 
 methods=["GET", "POST"])
def index():
    stock_symbols = get_stock_symbols()
    chart_url = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        chart_type = request.form["chart_type"]
        time_function = request.form["time_function"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        # Fetch and process data
        data = get_stock_data(symbol, time_function, start_date, end_date)

        # Generate chart
        chart_url = create_chart(data, chart_type)
    return render_template("index.html", symbols=stock_symbols, chart_url=chart_url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)