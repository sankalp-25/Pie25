from clickhouse_driver import Client
from polar.db import Connection, Table
from polar.fields import StringField, IntegerField, FloatField  # Add other field types as needed

# Step 1: Connect to ClickHouse
clickhouse_client = Client(
    host='159.89.171.188',
    database="stocksdb",
    port=8123,
    username='app_ro',
    password='Jij8GsT!WX1F'
)

# Step 2: Fetch Data from ClickHouse
clickhouse_query = "SELECT * FROM equity_price_1d"
clickhouse_data = clickhouse_client.execute(clickhouse_query)

# Step 3: Define the PostgreSQL Table Schema in Polar
class YourPostgresTable(Table):
    # Define the fields based on your table schema
    id = IntegerField(primary_key=True)
    name = StringField()
    value = FloatField()

# Step 4: Connect to PostgreSQL
pg_conn = Connection(
    dbname="postgres",
    user="postgres",
    password="BigBrainOmen@25",
    host="localhost",
    port="5432"
)

# Step 5: Insert Data into PostgreSQL
with pg_conn.transaction():  # Use transaction for batch insert
    for row in clickhouse_data:
        YourPostgresTable.insert(**dict(zip(YourPostgresTable._fields, row)))

print("Data transfer completed successfully!")
