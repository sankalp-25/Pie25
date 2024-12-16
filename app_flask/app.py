from flask import Flask, render_template, request, jsonify
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from shot2_1 import generate_sql_query
from pql_click_hit import DatabaseConnector
import time

app = Flask(__name__)

db_connector = DatabaseConnector()

current_date = datetime.strptime("2024-11-19", "%Y-%m-%d")

DEFAULT_TIMEFRAME = "Daily"
DEFAULT_AVG_VOLUME_PERIOD = "20-day"
DEFAULT_NEAR_RANGE_PERCENT = 5
settings = {
    "timeframe": DEFAULT_TIMEFRAME,
    "avg_volume_period": DEFAULT_AVG_VOLUME_PERIOD,
    "near_range_percent": DEFAULT_NEAR_RANGE_PERCENT,
    "current_date": current_date.strftime("%Y-%m-%d"),
    "current_date_minus_1_month": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
    "current_date_minus_1_week": (current_date - timedelta(days=7)).strftime("%Y-%m-%d"),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form.get('query')
    if user_query.lower() == 'thank_you':
        return jsonify({"message": "Thank you! Exiting the program."})

    try:
        sql_query = generate_sql_query(user_query, settings)
        query_result = db_connector.hit_sql(sql_query)
        result = query_result.to_dict(orient='records')
        return jsonify({"sql_query": sql_query, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
