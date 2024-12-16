import pandas as pd
from datetime import datetime, timedelta
from shot2_1 import generate_sql_query  
#from pql_hit import DatabaseConnector  
from pql_click_hit import DatabaseConnector  
import time

input_csv = "test/Benchmarks.csv"  # Fixed the path for consistency
#input_csv = r"C:/Users/Zelar/Documents/Strike_GPT/Pie25/test/OpenAi/Test-3.csv"
#output_csv_prefix = "output/3.5_Turbo/16-12/3.5_1." 
output_csv_prefix = "output/gemini_pro/16-12/Gpro_1." 

db_connector = DatabaseConnector()

questions_df = pd.read_csv(input_csv, encoding='latin1')

#current_date = datetime.strptime("2024-11-28", "%Y-%m-%d")
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


#take raw and processed output
#store 1st output 

for iteration in range(1):
    results = []
    for index, row in questions_df.iterrows():
        user_query = row['user_query']
        try:
            sql_query = generate_sql_query(user_query, settings)
            try:  
                query_result = db_connector.hit_sql(sql_query['Final SQL'])  
                if isinstance(query_result, pd.DataFrame):
                    results.append({
                        'user_query': user_query,
                        "Preprocessed": sql_query['Preprocessed'],
                        "Raw SQL": sql_query['Raw SQL'],
                        "Final SQL": sql_query['Final SQL'],
                        'result': []  
                    })
                else:
                    results.append({
                        'user_query': user_query,
                        "Preprocessed": sql_query['Preprocessed'],
                        "Raw SQL": sql_query['Raw SQL'],
                        "Final SQL": sql_query['Final SQL'],
                        'result': query_result
                    })
            except Exception as e:
                results.append({
                        'user_query': user_query,
                        "Preprocessed": sql_query['Preprocessed'],
                        "Raw SQL": sql_query['Raw SQL'],
                        "Final SQL": sql_query['Final SQL'],
                        'result': query_result
                })
        except Exception as e:
            results.append({
                    'user_query': user_query,
                    'SQL_query_generated': f"Error generating SQL: {str(e)}",
                    'result': "N/A"
                })

    # Save each iteration's results to a separate output file
    output_csv = f"{output_csv_prefix}{iteration + 1}.csv"
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)

    #print(f"Iteration {iteration + 1} complete. Results saved to {output_csv}")

#print("Automation complete for all 20 output files.")








'''
for iteration in range(1):  # Run the entire dataset 20 times
    results = []
    for index, row in questions_df.iterrows():
        user_query = row['user_query']  
        try:
            sql_query = generate_sql_query(user_query, settings)  
            try:
                query_result = db_connector.hit_sql(sql_query)  
                results.append({
                    'user_query': user_query,
                    'SQL_query_generated': sql_query,
                    'result': query_result.to_dict(orient='records')  
                })
            except Exception as e:
                results.append({
                    'user_query': user_query,
                    'SQL_query_generated': sql_query,
                    'result': f"Error executing query: {str(e)}"
                })
        except Exception as e:
            results.append({
                'user_query': user_query,
                'SQL_query_generated': f"Error generating SQL: {str(e)}",
                'result': "N/A"
            })
        time.sleep(5)

    # Save each iteration's results to a separate output file
    output_csv = f"{output_csv_prefix}{iteration + 1}.csv"
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)

    print(f"Iteration {iteration + 1} complete. Results saved to {output_csv}")

print("Automation complete for all 20 output files.")

'''