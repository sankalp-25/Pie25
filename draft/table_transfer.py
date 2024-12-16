import clickhouse_connect
import psycopg2

# Step 1: Connect to ClickHouse
ch_client = clickhouse_connect.get_client(
    host='159.89.171.188',
    database="stocksdb",
    port=8123,
    username='app_ro',
    password='Jij8GsT!WX1F'
)

# Step 2: Connect to PostgreSQL
pg_conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="BigBrainOmen@25",
    host="localhost",
    port="5432"
)
pg_cursor = pg_conn.cursor()

# Step 3: Create the target table in PostgreSQL
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS equity_prices_1d (
    date_time TIMESTAMP,
    security_code VARCHAR,
    open FLOAT8,
    high FLOAT8,
    low FLOAT8,
    close FLOAT8,
    volume BIGINT,
    version VARCHAR
);
""")
pg_conn.commit()

# Step 4: Fetch all data from ClickHouse
query = """
SELECT 
    date_time,
    security_code,
    open,
    high,
    low,
    close,
    CASE
        WHEN volume > 9223372036854775807 THEN 9223372036854775807
        WHEN volume < -9223372036854775808 THEN -9223372036854775808
        ELSE volume
    END AS volume,
    version
FROM 
    equity_prices_1d
WHERE 
    volume IS NOT NULL
"""
data = ch_client.query(query).result_rows

# Step 5: Insert all data into PostgreSQL
if data:
    placeholders = ', '.join(['%s'] * len(data[0]))
    insert_query = f"INSERT INTO equity_prices_1d (date_time, security_code, open, high, low, close, volume, version) VALUES ({placeholders})"
    
    try:
        pg_cursor.executemany(insert_query, data)
        pg_conn.commit()
        print(f"Inserted {len(data)} rows into PostgreSQL.")
    except psycopg2.Error as e:
        print(f"Error inserting data: {e}")
        pg_conn.rollback()
else:
    print("No data fetched from ClickHouse.")

# Step 6: Close connections
pg_cursor.close()
pg_conn.close()
ch_client.close()
