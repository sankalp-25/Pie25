import os
import json
from datetime import datetime, timedelta
from API_keys.gemini_API import generate_text
# from API_keys.openai_API_API import generate_text
# from API_keys.perplexity_API_API import generate_text
# from API_keys.cohere_API import generate_text


SUPPORTED_TIMEFRAMES = ["5min", "15min", "30min", "45min", "75min", "120min", "240min", "125min", 
                        "Hourly", "Daily", "Weekly", "Monthly", "Quarterly"]

DEFAULT_TIMEFRAME = "Daily"
DEFAULT_AVG_VOLUME_PERIOD = "20-day"
DEFAULT_NEAR_RANGE_PERCENT = 5


def load_company_symbols(json_file):
    with open(json_file, "r") as file:
        return json.load(file)

def generate_sql_query(user_query, company_map, settings):
    prompt = f"""
You are a Senior Data engineer who is expert in SQL and who also is investing in stock market for the past 30 years. Your task is to convert any natural language query about stock market data into a valid SQL query.

The following is are the columns in the table 'consolidated_macd'
- date
- opening_price
- closing_price
- highest_price
- lowest_price
- adjacent_close
- volume
- company_name 

Here are some important rules to follow:
1. Default time-period is "{settings['timeframe']}".
2. For calculating AVERAGE VOLUME use 20-days of data. 
3. Supported timeframes are: {', '.join(SUPPORTED_TIMEFRAMES)}.
4. If no specific date is mentioned, consider the current date or the most recent price as the reference.
5. For rolling periods (like "last 1 month"), use a dynamic date range. For example, "last 1 month" from today means the period from {settings['current_date_minus_1_month']} to {settings['current_date']}.
6. For comparisons, use percentages unless explicitly asked for absolute values.


Instructions while generating SQL query:
1. STRICITLY provide only executable SQL query
2. DO NOT ADD any REDUNDANCY steps in the process
3. DO NOT ADD CONCLUSIONS, SUMMAMRY, NOTES at the END of PROCESS 
4. DO NOT USE SINGLE COLONS OR DOUBLE COLONS TO THE TABLE NAME
5. DO NOT ADD ```sql AT THE START AND ``` AT THE END OF THE OUTPUT

User Query: "{user_query}"
SQL Query:
"""
    return generate_text(prompt)

def validate_user_query(user_query, company_map):
    valid_company = None
    for company_name in company_map.keys():
        if company_name.lower() in user_query.lower():
            valid_company = company_name
            break

    timeframe = DEFAULT_TIMEFRAME
    for tf in SUPPORTED_TIMEFRAMES:
        if tf.lower() in user_query.lower():
            timeframe = tf
            break

    return {"company": valid_company, "timeframe": timeframe}

def main_temp():
    json_file = "C&S.json"
    company_map = load_company_symbols(json_file)

    current_date = datetime.now().date()
    settings = {
        "timeframe": DEFAULT_TIMEFRAME,
        "avg_volume_period": DEFAULT_AVG_VOLUME_PERIOD,
        "near_range_percent": DEFAULT_NEAR_RANGE_PERCENT,
        "current_date": current_date.strftime("%Y-%m-%d"),
        "current_date_minus_1_month": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
        "current_date_minus_1_week": (current_date - timedelta(days=7)).strftime("%Y-%m-%d"),
    }

    print("Welcome to the Stock Market Chatbot!")
    print('Enter your queries. Type "thank_you" to end the chat.\n')

    while True:
        user_query = input("Your Question: ").strip()

        if user_query.lower() == "thank_you":
            print("Thank you for using the Stock Market Chatbot. Goodbye!")
            break

        details = validate_user_query(user_query, company_map)

        if not details["company"]:
            print("No specific company mentioned. Proceeding with general query.\n")

        if details["timeframe"] not in SUPPORTED_TIMEFRAMES:
            print(f"Unsupported timeframe. Available timeframes are: {', '.join(SUPPORTED_TIMEFRAMES)}.\n")
            continue

        sql_query = generate_sql_query(user_query, company_map, settings)
        print("\n")
        print(sql_query)
        print("\n")
        # print("################ End of the output ###################")
        # print(f"Note: Default settings used - Timeframe: {settings['timeframe']}, "
        #       f"20-Day Average Volume, Near Range: {settings['near_range_percent']}%.\n")

if __name__ == "__main__":
    main_temp()
