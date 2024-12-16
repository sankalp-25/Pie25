import pandas as pd
from datetime import datetime, timedelta
from shot2_1 import generate_sql_query
from pql_click_hit import DatabaseConnector
import time

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

print("Starting the question-answer loop. Type 'thank_you' to stop.")

while True:
    user_query = input("Enter your query (or type 'thank_you' to stop): ") #Taking input
    
    if user_query.lower() == 'thank_you':
        print("Thank you! Exiting the program.")
        break

    try:
        sql_query = generate_sql_query(user_query, settings)
        
        try:
            query_result = db_connector.hit_sql(sql_query['Final SQL'])
            print(f"Query Result: ",query_result) #output
        except Exception as e:
            print(f"Error executing query: {str(e)}")
    except Exception as e:
        print(f"Error generating SQL: {str(e)}")

    # Optionally, add a short delay between queries
    time.sleep(5)

print("Program has exited.")
