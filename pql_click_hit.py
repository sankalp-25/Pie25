import os
import pandas as pd
import clickhouse_connect

class DatabaseConnector:
    def __init__(self, database="db_strike", user="strike_user1", password='Strike123$', host="202.131.150.31", port=8123):
    #def __init__(self, database="default", user="default", password='', host="localhost", port=8123):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database
        )

    def hit_sql(self, sql_query):
        try:
            print("***********************************************************************")
            print(sql_query)
            print("***********************************************************************")
            result = self.client.query(sql_query)
            results = result.result_rows
            column_names = result.column_names
            df = pd.DataFrame(results, columns=column_names)
            #df=pd.DataFrame() #remove this later, do not foget
            print(df)
            return df

        except Exception as e:
            return(f"{e}")

    def close(self):
        self.client.close()

# k=DatabaseConnector()
# p=k.hit_sql('''SELECT DISTINCT "company_name", "high"
# FROM "equity_prices_1d" AS ep
# JOIN "master_prime_1d" AS mp ON ep."security_code" = mp."security_code"
# WHERE ep."date_time" = (SELECT MAX("date_time") FROM "equity_prices_1d")
# AND ((ep."high" / (SELECT MAX(ep_inner."high") FROM "equity_prices_1d" AS ep_inner WHERE ep_inner."date_time" >= '2023-11-19') - 1) * 100) >= 0.0''')
# print(p)