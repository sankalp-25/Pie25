import psycopg2
import pandas as pd
# Database connection parameters
db_params = {
    'host': 'localhost',           # e.g., 'localhost'
    'database': 'postgres',     # Replace with your database name
    'user': 'postgres',        # Replace with your username
    'password': 'BigBrainOmen@25',    # Replace with your password
    'port': '5432'                  # Default PostgreSQL port
}

# Read the CSV file
csv_file = 'output2-1732875363035.csv'
df = pd.read_csv(csv_file)

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Create table query dynamically from DataFrame
    table_name = 'your_table_name'
    columns = ', '.join([f'{col} TEXT' for col in df.columns])  # All columns as TEXT for simplicity

    create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns});'
    cur.execute(create_table_query)
    conn.commit()

    # Insert data into the table
    for _, row in df.iterrows():
        insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(row))})"
        cur.execute(insert_query, tuple(row))
    
    conn.commit()
    print(f"Data from {csv_file} successfully inserted into {table_name}.")

except Exception as e:
    print("Error:", e)
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()