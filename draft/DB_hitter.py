import psycopg2
import os
def run():
    db_config = {
                "dbname": "postgres",
                "user": "postgres",
                "password": os.getenv("DB_PASSWORD"),
                "host": "localhost",
                "port": 5432
            }

    conn = psycopg2.connect(db_config)
    cur = conn.cursor()

    # Execute the query
    #cur.execute(sql_query)
    cur.execute("SELECT company_name FROM consolidated_macd WHERE close >= 0.95 * (SELECT MAX(high) FROM consolidated_macd WHERE date >= date('now', '-52 weeks'))")
    results = cur.fetchall()
    print(results)
run()