import os
import psycopg2
import pandas as pd

class DatabaseConnector:
    def __init__(self, dbname="postgres", user="postgres", password=None, host="localhost", port="5432"):
        self.db_config = {
            "dbname": dbname,
            "user": user,
            "password": password or os.getenv("DB_PASSWORD"),
            "host": host,
            "port": port
        }

    def hit_sql(self, sql_query):
        print(sql_query)
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute(sql_query)
            #cur.execute("SELECT company_name FROM consolidated_macd WHERE close >= 0.95 * (SELECT MAX(high) FROM consolidated_macd WHERE date >= date('now', '-52 weeks'))")
            results = cur.fetchall()
            print(results)
            column_names = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=column_names)

            print("DataFrame Created:")
            print(df)
            cur.close()
            conn.close()

            return df

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
