import os
import psycopg2
from shot2_1 import main_temp 
import pandas as pd

def hit_sql():
    db_config = {
        "dbname": "postgres",
        "user": "postgres",
        "password": os.getenv("DB_PASSWORD"),
        "host": "localhost",
        "port": "5432",
    }

    query  = main_temp()
    print(query)

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute(SQL_query)
        results = cur.fetchall()
        
        column_names = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=column_names)
        
        print("DataFrame Created:")
        print(df)
        
        cur.close()
        conn.close()

    except Exception as e:
        (f"An error occurred: {e}")

if __name__ == "__main__":
    hit_sql()