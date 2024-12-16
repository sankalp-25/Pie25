import pandas as pd
import clickhouse_connect as Client
import os
import time
# Initialize the ClickHouse client
client = Client.get_client(database="db_strike", user="strike_user1", password='Strike123$', host="202.131.150.31", port=8123)#os.getenv("CH_P"))
#client = Client.get_client(database="default", user="default", password='', host="localhost", port=8123)#os.getenv("CH_P"))

# Load the Excel file
#excel_file = r"C:\Users\Zelar\Documents\Strike_GPT\Pie25\output\gemini_pro\13-12\Gpro_1.311.csv"  # Replace with your actual file name
#excel_file=r'C:\Users\Zelar\Documents\Strike_GPT\Pie25\output\gemini_pro\13-12\format_testing_Gpro.csv'
excel_file=r"C:\Users\Zelar\Documents\Strike_GPT\Pie25\output\3.5_Turbo\13-12\3.5_1.71.csv"
df = pd.read_csv(excel_file, encoding='latin1')

# Iterate through each row
for index, row in df.iterrows():
    sql_query = row['3rd output']  # The SQL query
    try:
        # Execute the query
        result = client.query(str(sql_query))
        # Extract the result and convert it to a string if needed
        print('working fine untill here mama - 19')
        df.at[index, 'Result_final'] = "success"
        print('working fine untill here mama - 21')
    except Exception as e:
        # Handle errors and log them in the result column
        df.at[index, 'Result_final'] = 'failed because' +"\n"+f"{str(e)}"
    time.sleep(6)
# Save the updated DataFrame back to the Excel file
df.to_csv(excel_file, index=False)

print("SQL queries executed and results updated in the Excel file.")
