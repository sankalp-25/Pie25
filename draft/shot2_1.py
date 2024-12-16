import os
import json
from datetime import datetime, timedelta, date
#from API_keys.gemini_API import generate_text
from API_keys.openai_API import generate_text
#from API_keys.perplexity_API import generate_text
#from API_keys.cohere_API import generate_text
#from API_keys.mistral_API import generate_text
from Company_Name_Nom import get_short_company_name

SUPPORTED_TIMEFRAMES = ["5min", "15min", "30min", "45min", "75min", "120min", "240min", "125min", 
                        "Hourly", "Daily", "Weekly", "Monthly", "Quarterly"]

#current_date = datetime.now().date()
current_date = datetime.strptime("2024-11-19", "%Y-%m-%d")
#current_date = datetime.strptime("2024-11-28", "%Y-%m-%d")



def generate_sql_query(user_query, settings):
    short_company_name = get_short_company_name(user_query)
    # Prompt 1: Pre-processing Natural Language
    prompt1 = f"""
    You are an intelligent assistant skilled at interpreting and structuring natural language queries into a structured format. 

    Your task is to pre-process any user query related to stock market data and output the extracted intent and relevant details in a structured format. The output must be precise, covering:
    - **UserQuery**: {user_query}
    - **Intent**: What the user wants to achieve (e.g., retrieve, compare, calculate, filter).
    - **Table**: Which table(s) are relevant (`master_prime_1d`, `equity_prices_1d`).
    - **Columns**: Specific columns required for the query (e.g., `company_name`, `high`).
    - **Filters**: Any conditions or filters applied (e.g., date range, stock name, index).
    - **Grouping**: Whether the query requires aggregation or grouping.
    - **Timeframe**: Any date range or specific time criteria, default to "{settings['timeframe']}" if not provided.

    The database contains two tables named 'master_prime_1d' and 'equity_prices_1d' with the following schema

    ### Database Structure
    #### Table: **`master_prime_1d`**
    - **`security_code`**: A unique code assigned to each listed security (e.g., stock, bond).  
    - **`company_name`**: The full legal name of the company (e.g., Reliance Power Limited, Tata Motors Limited).  
    - **`short_company_name`**: The calculated symbol of the stock (e.g., RPOWER, TATAMOTORS).  
    - **`industry_name`**: The name of the industry (e.g., IT, Pharmaceuticals).  
    - **`broad_industry_name`**: The broader industry category (e.g., Technology, Healthcare).  
    - **`major_sector_name`**: The major sector (e.g., Services, Manufacturing).  
    - **`index_name`**: The stock market index name (e.g., Nifty 500, BSE Sensex).  

    #### Table: **`equity_prices_1d`**
    - **`date_time`**: The timestamp for the recorded trading day.  
    - **`security_code`**: A unique identifier for the traded security.  
    - **`open`**: The opening price of the security on a given day.  
    - **`high`**: The highest price of the security during the trading day.  
    - **`low`**: The lowest price of the security during the trading day.  
    - **`close`**: The closing price of the security on that day.  
    - **`volume`**: The number of shares or units traded during the day.  
    - **`version`**: A record versioning number for data integrity. 

    Rules:
    1. Refer to the schemas for `master_prime_1d` and `equity_prices_1d`.
    2. If any ambiguity exists, state `Ambiguity: [detail]`.
    3. Do not generate SQL queries; your output must only provide structured data.
    
    important note:
        1. NSE is National Stock Exchange but not an index_name
    
    **Example Output:**
    {{
      "User_Query":
      "Intent": "Retrieve",
      "Table": ["equity_prices_1d"],
      "Columns": ["high", "low", "date_time"],
      "Filters": {{
        "date_range": ["2024-11-01", "2024-11-30"],
        "industry_name": "Pharmaceuticals"
      }},
      "Grouping": false,
      "Timeframe": "2024-11"
    }}
    ###STRICTILY RETURN THE OUTPUT IN A DICTIONARY###
    User Query: {user_query}
    Output:
    """
    
    x_raw = generate_text(prompt1)
    x=json.loads(x_raw)
    #Assuming x is your dictionary
    if 'index_name' in x.get('Filters', {}):
        if x['Filters']['index_name'] == 'NSE' or x['Filters']['index_name'] == ['NSE']:
            del x['Filters']['index_name']  # Delete the whole key if it is exactly 'NSE'
        elif 'NSE' in x['Filters']['index_name']:
            x['Filters']['index_name'] = x['Filters']['index_name'].replace('NSE', '')  # Remove 'NSE' if it is part of the string

    # Prompt 2: SQL Query Generation
    prompt2 = f"""
    You are a Senior Data Engineer skilled at generating optimized SQL queries for ClickHouse databases.

    The database contains two tables named 'master_prime_1d' and 'equity_prices_1d' with the following schema
    
    ### Database Structure
    #### Table: **`master_prime_1d`**
    - **`security_code`**: A unique code assigned to each listed security (e.g., stock, bond).  
    - **`company_name`**: The full legal name of the company (e.g., Reliance Power Limited, Tata Motors Limited).  
    - **`short_company_name`**: The calculated symbol of the stock (e.g., RPOWER, TATAMOTORS).  
    - **`industry_name`**: The name of the industry (e.g., IT, Pharmaceuticals).  
    - **`broad_industry_name`**: The broader industry category (e.g., Technology, Healthcare).  
    - **`major_sector_name`**: The major sector (e.g., Services, Manufacturing).  
    - **`index_name`**: The stock market index name (e.g., Nifty 500, BSE Sensex).  

    #### Table: **`equity_prices_1d`**
    - **`date_time`**: The timestamp for the recorded trading day.  
    - **`security_code`**: A unique identifier for the traded security.  
    - **`open`**: The opening price of the security on a given day.  
    - **`high`**: The highest price of the security during the trading day.  
    - **`low`**: The lowest price of the security during the trading day.  
    - **`close`**: The closing price of the security on that day.  
    - **`volume`**: The number of shares or units traded during the day.  
    - **`version`**: A record versioning number for data integrity.

    Your task is to convert structured data from a pre-processed query into a valid, executable, and optimized SQL query. Adhere strictly to the following rules:
    - Use only the `master_prime_1d` and `equity_prices_1d` tables.
    - Follow the schemas for each table and ensure column-table integrity.
    - Apply filters, groupings, and aggregations exactly as specified in the structured data.
    - Use `JOIN` operations for cross-table queries.
    - Handle NULL values with `CASE WHEN` or `COALESCE`.
    - Always default to double quotes for table and column names.
    - Avoid correlated subqueries and use efficient JOINs or aggregations.
    Important Rules:
        1. Default Timeframe: If the user does not specify a timeframe, use "{settings['timeframe']}" as the default.
        2. Average Volume: For any query involving average volume, the default period is the last 20 days unless stated otherwise.
        3. Supported Timeframes: Valid timeframes include: {', '.join(SUPPORTED_TIMEFRAMES)}.
        4. Date Reference: Use the current date ({current_date}) and calculate days/weeks/months/years accoding to the query.
            valid date format  : "2024-11-19"
            invalid date format: "2024-11-19 00:00:00"
        5. Dynamic Periods: For phrases like "last 1 month," dynamically calculate the date range using {settings['current_date_minus_1_month']} to {settings['current_date']}.
        6. Comparison Values: For all comparisons, default to percentages unless the user explicitly specifies absolute values.
        7. While checking for index_name do not directily check with cell value but check whether that string is present in that column values using **LIKE**.
        8. When the detailes are asked about the stock name or list of stocks, do not provide security_code; strictily provide company_name only.
        9. While you are selecting company_name, make sure to use **DISTINCT**.
        10. When combining results with `UNION`, specify either `UNION ALL` (to include duplicates) or `UNION DISTINCT` (to remove duplicates).
        11. Whlie performing division, use WHERE CASE WHEN <CONDITION> <OPERATION> ELSE <OPERATION> to aviod ILLEGAL_DIVISION error 
        12. Ensure **`LIKE` operators** are only used with string-type columns. Avoid applying `LIKE` on non-string fields such as `security_code` or `volume`.

    Input Structured Data:
    {x}

    Generated SQL Query:
    """

    # Generate the SQL query based on the structured data
    output = generate_text(prompt2)

    if output[:6] == '```sql':
        final_output = output[6:-4]
    else:
        final_output=output

    #return output
    return [x,output, final_output]

    timeframe = DEFAULT_TIMEFRAME
    for tf in SUPPORTED_TIMEFRAMES:
        if tf.lower() in user_query.lower():
            timeframe = tf
            break

    return {"company": valid_company, "timeframe": timeframe}

"""
Important note:
Make sure to declare tables/varibles that are being used in the query.
-Valid SQL query :
    SELECT DISTINCT "company_name"
    FROM "master_prime_1d"
    JOIN "equity_prices_1d" ON "master_prime_1d"."security_code" = "equity_prices_1d"."security_code"
    WHERE "equity_prices_1d"."close" >= 0.95 *
    (SELECT max("close")
    FROM "equity_prices_1d","master_prime_1d"
    WHERE "equity_prices_1d"."security_code" = "master_prime_1d"."security_code");
-Invalid SQL query:
    SELECT DISTINCT "company_name"
    FROM "master_prime_1d"
    JOIN "equity_prices_1d" ON "master_prime_1d"."security_code" = "equity_prices_1d"."security_code"
    WHERE "equity_prices_1d"."close" >= 0.95 *
    (SELECT max("close")
    FROM "equity_prices_1d"
    WHERE "security_code" = "master_prime_1d"."security_code");

    Explination:
    Here since the nested select doesn't know about global "master_prime_1d" table it will throw an error. Stricitly declare the tables/varibles that are being used inside the nest.

    where the question is briefly described and then that description is given to other prompt which can generate sql query effectively
    """
"""
You are a Senior Data Engineer with 30 years of experience in indian stock market investments. Your task is to convert any natural language query about stock market data into a valid and optimized Clickhouse query.

  In the database, there is only two table 'master_prime_1d' and 'equity_prices_1d'

  Schema: **master_prime_1d**
      *security_code*: A unique code assigned to each listed security (e.g., stock, bond).
      *company_name*: the full legal name of the company the stock belongs to. (e.g., Reliance Power Limited, Tata Motors Limited etc)
      *short_company_name*: the symbol of the stock that is calculated.  (e.g., RPOWER, TATAMOTORS etc)
      *industry_name*: The name of the industry (e.g., IT, Pharmaceuticals).
      *broad_industry_name*: The name of the broader industry category (e.g., Technology, Healthcare).
      *major_sector_name*: The name of the major sector (e.g., Services, Manufacturing).
      *index_name*: The name of the stock market index (e.g., Nifty 500, BSE Sensex).

  ---
        
  Schema: **equity_prices_1d**
      *date_time*: The timestamp for the recorded trading day (e.g., daily close).
      *security_code*: A unique identifier for the traded security.
      *open*: The opening price of the security on a given day.
      *high*: The highest price of the security during the trading day.
      *low*: The lowest price of the security during the trading day.
      *close*: The closing price of the security on that day.
      *volume*: The number of shares or units traded during the day.
      *version*: A record versioning number for data integrity and tracking.
  Note:
  Strictily stick to the table and its appropriate columns, do not try to access one colum from another table

  Instructions:
  1. **Use Double Quotes for Table Names**: PROVIDE THE TABLE NAME WITHIN DOUBLE QUOTES IN THE SQL QUERY THAT YOU ARE GENERATING
    - Example: 
        SELECT "short_company_name" FROM "master_prime_1d"

  2. **Maintain Table-Column Integrity**: DO NOT CALL A COLUMN NAME WHICH BELONGS TO TABLE1 FROM TABLE2.
      - VALID CALL : SELECT "short_company_name" FROM "master_prime_1d"
      - INVALID CALL : SELECT "short_company_name" FROM "equity_prices_1d"

  3. **Cross-Table Queries**: When using columns from both tables, reference columns explicitly with their respective table names.
    - Example: 
      SELECT "master_prime_1d"."company_name", "equity_prices_1d"."close"
      FROM "master_prime_1d"
      JOIN "equity_prices_1d" ON "master_prime_1d"."security_code" = "equity_prices_1d"."security_code"

  4. **NSE is not a index_name** : If the query contains the word **'NSE'**, while generating sql query consider all index_name values.
    -Example: Provide list of all index names in NSE
            - **Valid SQL query**:
              SELECT index_name FROM "master_prime_1d"
            - **Invalid SQL query**:
              SELECT index_name FROM "master_prime_1d" WHERE index_name="%%NSE%%"

  5. **Use short_company_name :** '{short_company_name}' **only if needed.

  6. **Avoid correlated subqueries entirely**:Instead, restructure queries to use joins or aggregate subqueries with groupings, ensuring they are independent. Therefore instead of correlated subquery restructure the query to use join instead.
    Example:
    a.
    - INVALID: 
              SELECT employee_id, salary
              FROM employees e
              WHERE salary > (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id);
    - VALID: 
              SELECT e.employee_id,e.salary,e.department_id
              FROM employees e
              JOIN 
              (SELECT department_id, AVG(salary) AS avg_salary
                  FROM employees
                  GROUP BY department_id
              ) d 
              ON e.department_id = d.department_id
              WHERE e.salary > d.avg_salary;
      b.
      - INVALID:
            SELECT DISTINCT "company_name"
            FROM "master_prime_1d"
            JOIN "equity_prices_1d" ON "master_prime_1d"."security_code" = "equity_prices_1d"."security_code"
            WHERE "low" < (SELECT "low" FROM "equity_prices_1d" WHERE "date_time" = '2024-09-13' AND "equity_prices_1d"."security_code" = "equity_prices_1d"."security_code")
            AND "date_time" = '2024-09-20';
      - VALID:
            SELECT DISTINCT mp."company_name"
            FROM master_prime_1d AS mp
            JOIN equity_prices_1d AS ep1 
                ON mp.security_code = ep1.security_code
            JOIN equity_prices_1d AS ep2 
                ON ep1.security_code = ep2.security_code
            WHERE ep2.date_time = '2024-09-13'
              AND ep1.date_time = '2024-09-20'
              AND ep1.low < ep2.low;

  9. Always **use `CASE WHEN` or `COALESCE`** to handle potential NULL values in queries.
      - Example: Instead of `column > value`, use `CASE WHEN column IS NOT NULL THEN column > value ELSE FALSE END`.

  10. Ensure **`LIKE` operators** are only used with string-type columns. Avoid applying `LIKE` on non-string fields such as `security_code` or `volume`.         
            
  . **The clickhouse version that is being used is  24.12.1.850**

  Important Rules:
  1. Default Timeframe: If the user does not specify a timeframe, use "{settings['timeframe']}" as the default.
  2. Average Volume: For any query involving average volume, the default period is the last 20 days unless stated otherwise.
  3. Supported Timeframes: Valid timeframes include: {', '.join(SUPPORTED_TIMEFRAMES)}.
  4. Date Reference: Use the current date ({current_date}) and calculate days/weeks/months/years accoding to the query.
      valid date format  : "2024-11-19"
      invalid date format: "2024-11-19 00:00:00"
  5. Dynamic Periods: For phrases like "last 1 month," dynamically calculate the date range using {settings['current_date_minus_1_month']} to {settings['current_date']}.
  6. Comparison Values: For all comparisons, default to percentages unless the user explicitly specifies absolute values.
  7. While checking for index_name do not directily check with cell value but check whether that string is present in that column values using **LIKE**.
  8. When the detailes are asked about the stock name or list of stocks, do not provide security_code; strictily provide company_name only.
  9. While you are selecting company_name, make sure to use **DISTINCT**.
  10. When combining results with `UNION`, specify either `UNION ALL` (to include duplicates) or `UNION DISTINCT` (to remove duplicates).
  11. Whlie performing division, use WHERE CASE WHEN <CONDITION> <OPERATION> ELSE <OPERATION> to aviod ILLEGAL_DIVISION error 
  12. Ensure **`LIKE` operators** are only used with string-type columns. Avoid applying `LIKE` on non-string fields such as `security_code` or `volume`.

  ### **ClickHouse Aggregate Functions**
  #### **Basic Aggregates**
  - `avg(column)`: Calculates the average value of a numeric column.  
    - **Syntax**: `SELECT avg(column_name) FROM table_name;`  

  - `sum(column)`: Computes the total sum of values in a column.  
    - **Syntax**: `SELECT sum(column_name) FROM table_name;`  

  - `count(column)`: Counts rows or specific non-NULL values in a column.  
    - **Syntax**: `SELECT count(*) FROM table_name;`  
    - **Alternative**: `SELECT count(column_name) FROM table_name;`  

  - `min(column)`: Retrieves the smallest value in a column.  
    - **Syntax**: `SELECT min(column_name) FROM table_name;`  

  - `max(column)`: Retrieves the largest value in a column.  
    - **Syntax**: `SELECT max(column_name) FROM table_name;`  

  ---

  #### **Statistical Functions**
  - `stddevPop(column)`: Computes population standard deviation.  
    - **Syntax**: `SELECT stddevPop(column_name) FROM table_name;`  

  - `stddevSamp(column)`: Computes sample standard deviation.  
    - **Syntax**: `SELECT stddevSamp(column_name) FROM table_name;`  

  ---

  #### **Percentile and Quantile Functions**
  - `quantile(level)(column)`: Approximates a specified quantile (e.g., median).  
    - **Syntax**: `SELECT quantile(0.5)(column_name) FROM table_name;`  

  - `quantiles(level1, level2, ...)(column)`: Computes multiple quantiles simultaneously.  
    - **Syntax**: `SELECT quantiles(0.25, 0.5, 0.75)(column_name) FROM table_name;`  

  - `quantileExact(level)(column)`: Calculates exact quantiles.  
    - **Syntax**: `SELECT quantileExact(0.95)(column_name) FROM table_name;`  

  ---

  #### **Array Aggregates**
  - `groupArray(column)`: Collects column values into an array.  
    - **Syntax**: `SELECT groupArray(column_name) FROM table_name;`  

  ---

  #### **Uniqueness Estimations**
  - `uniq(column)`: Estimates the number of unique values in a column.  
    - **Syntax**: `SELECT uniq(column_name) FROM table_name;`  

  - `uniqExact(column)`: Counts unique values exactly.  
    - **Syntax**: `SELECT uniqExact(column_name) FROM table_name;`  

  ---

  #### **Example Query**

  SELECT 
      avg(volume) AS average_volume, 
      quantile(0.5)(volume) AS median_volume, 
      quantiles(0.25, 0.5, 0.75)(volume) AS quartiles, 
      groupArray(volume) AS volume_array, 
      uniq(security_code) AS unique_codes 
  FROM equity_prices_1d;

  SQL Query Generation Rules:
  ###GENERATE ONLY AN EXECUTABLE ANSI SQL BY DEFAULT###
  ###DO NOT ADD COMMENTS TO THE QUERY###
  ###AVOID UNNECESSARY STEPS, REDUNDANT CALCULATIONS, OR EXTRANEOUS COMMENTS.###
  ###ENSURE THE QUERY ADHERES STRICTLY TO THE USER’S REQUIREMENTS WITHOUT ASSUMPTIONS OR ADDED CONTEXT.###


  User Query: {user_query}
  Generated SQL Query: 

"""