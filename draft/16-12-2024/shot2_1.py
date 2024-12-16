import os
import json
import re
from datetime import datetime, timedelta, date
from API_keys.gemini_API import generate_text
#from API_keys.openai_API import generate_text
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
You are an expert data analyst specializing in stock market data. Your task is to preprocess a given natural language query to extract structured components for SQL query generation.

Convert {user_query} into a structured format based on the following:

IMPORTANT Instructions:
1. **Understand the Query's Intent**: Determine the query's goal (e.g., retrieve specific data, aggregate values, filter data by conditions).
2. **Extract Components**: 
   - **Tables**: Identify which tables (`master_prime_1d` or `equity_prices_1d`) are needed.
   - **Columns**: List the columns to retrieve, aggregate, or filter.
   - **Conditions**: Extract filters or constraints (e.g., date ranges, specific companies, industry names).
   - **Joins**: Identify if a join is required and specify the joining condition.
   - **Aggregations**: Identify if aggregate functions (e.g., `avg`, `sum`, `max`) are required.
   - **Sorting/Grouping**: Specify any sorting, grouping, or limit requirements.

3. **Reformat**: Provide a structured output:
   - **Intent**: [Brief summary of the query's goal]
   - **Required Tables**: [List of tables]
   - **Columns**: [List of columns needed]
   - **Conditions**: [List of conditions]
   - **Joins**: [Join requirements]
   - **Aggregations**: [Aggregations, if any]
   - **Sorting/Grouping**: [Details, if applicable]

### Database Structure
#### Table: **`master_prime_1d`**
- **`security_code`**: Unique code for each listed security (e.g., stock, bond).
- **`company_name`**: Full legal name of the company (e.g., Reliance Power Limited).
- **`short_company_name`**: Symbol of the stock (e.g., RPOWER).
- **`industry_name`**: Industry name (e.g., IT, Pharmaceuticals).
- **`broad_industry_name`**: Broader industry category (e.g., Technology, Healthcare).
- **`major_sector_name`**: Major sector (e.g., Services, Manufacturing).
- **`index_name`**: Stock market index name (e.g., Nifty 500).

#### Table: **`equity_prices_1d`**
- **`date_time`**: Timestamp for the recorded trading day.
- **`security_code`**: Unique identifier for traded security.
- **`open`**: Opening price of the security.
- **`high`**: Highest price during the trading day.
- **`low`**: Lowest price during the trading day.
- **`close`**: Closing price of the security.
- **`volume`**: Number of shares traded.
- **`version`**: Record version number for data integrity.
STRICTILY DO NOT SELECT A COLUMN WHICH BELONGS TO SOME OTHER TABLE, STRICTILY MAKE SURE YOU MAINTAIN TABLE-COLUMN INTEGRITY 

Example:
Natural Language Query: "Show the average closing price of stocks in the IT industry between 01-11-2024 to 28-11-2024."
Preprocessed Output:
- **Intent**: Retrieve the average closing price for IT industry stocks over the last 30 days.
- **Required Tables**: `master_prime_1d`, `equity_prices_1d`
- **Columns**: `close`, `industry_name`
- **Conditions**: `industry_name = 'IT'`, `date_time BETWEEN '2024-11-01' AND '2024-11-30'`
- **Joins**: `master_prime_1d.security_code = equity_prices_1d.security_code`
- **Aggregations**: `avg(close)`
- **Sorting/Grouping**: None


    """
    #x=generate_text(prompt1)
    x_raw = generate_text(prompt1)
    if(len(x_raw)!=0):
        x_raw=re.sub('NSE', '', x_raw, flags=re.IGNORECASE)
    #     x=json.loads(x_raw)
    #     #Assuming x is your dictionary
    #     if 'index_name' in x.get('Filters', {}):
    #         if x['Filters']['index_name'] == 'NSE' or x['Filters']['index_name'] == ['NSE']:
    #             del x['Filters']['index_name']  # Delete the whole key if it is exactly 'NSE'
    #         elif 'NSE' in x['Filters']['index_name']:
    #             x['Filters']['index_name'] = x['Filters']['index_name'].replace('NSE', '')  # Remove 'NSE' if it is part of the string

    # Prompt 2: SQL Query Generation
    prompt2 = f"""
        You are a Senior Data Engineer with 30 years of experience in Indian stock market investments. Your task is to generate a valid and optimized ClickHouse SQL query based on the provided structured components. Follow these steps:
        Covert {x_raw} into SQL query for which the user query is {user_query} and only provide SQL query as output
        
        1. Use the structured components as input.
        2. Write the SQL query strictly adhering to the following rules:
            - Always use double quotes for table and column names.
            - Maintain table-column integrity.
            - Use explicit joins when combining data from multiple tables.
            - Avoid correlated subqueries.
            - Handle NULL values using `CASE WHEN` or `COALESCE`.
            - Format dates in "YYYY-MM-DD" format.
        3. Database Schema
            #### **Table: `master_prime_1d`**
            - **`security_code`**: Unique identifier for securities (e.g., stocks, bonds).
            - **`company_name`**: Full legal company name (e.g., Reliance Power Limited).
            - **`short_company_name`**: Stock symbol (e.g., RPOWER).
            - **`industry_name`**: Industry (e.g., IT, Pharmaceuticals).
            - **`broad_industry_name`**: Broader category (e.g., Technology).
            - **`major_sector_name`**: Sector (e.g., Manufacturing).
            - **`index_name`**: Stock market index (e.g., Nifty 500).

            #### **Table: `equity_prices_1d`**
            - **`date_time`**: Trading day timestamp.
            - **`security_code`**: Security identifier.
            - **`open`**: Opening price.
            - **`high`**: Highest price.
            - **`low`**: Lowest price.
            - **`close`**: Closing price.
            - **`volume`**: Units traded.
            - **`version`**: Record version for integrity.
            STRICTILY DO NOT SELECT A COLUMN WHICH BELONGS TO SOME OTHER TABLE, STRICTILY MAKE SURE YOU MAINTAIN TABLE-COLUMN INTEGRITY 
            4. IMPORTANT INSTRUCTIONS
                1. Default Timeframe: If the user does not specify a timeframe, use "{settings['timeframe']}" as the default.
                2. Average Volume: For any query involving average volume, the default period is the last 20 days unless stated otherwise.
                3. Supported Timeframes: Valid timeframes include: {', '.join(SUPPORTED_TIMEFRAMES)}.
                4. Date Reference: Use the current date ({current_date}) and calculate days/weeks/months/years accoding to the query.
                valid date format : "2024-11-19"
                invalid date format: "2024-11-19 00:00:00"
                5. Dynamic Periods: For phrases like "last 1 month," dynamically calculate the date range using {settings['current_date_minus_1_month']} to {settings['current_date']}.
                6. Comparison Values: For all comparisons, default to percentages unless the user explicitly specifies absolute values.
                7. While checking for index_name do not directily check with cell value but check whether that string is present in that column values using **LIKE**.
                8. When the detailes are asked about the stock name or list of stocks, do not provide security_code; strictily provide company_name only.
                9. While you are selecting company_name, make sure to use **DISTINCT**.
                10. When combining results with UNION, specify either UNION ALL (to include duplicates) or UNION DISTINCT (to remove duplicates).
                11. Whlie performing division, use WHERE CASE WHEN <CONDITION> <OPERATION> ELSE <OPERATION> to aviod ILLEGAL_DIVISION error
                12. Ensure **LIKE operators** are only used with string-type columns. Avoid applying LIKE on non-string fields such as security_code or volume.
                13. Use short_company_name  '{short_company_name}' if needed while generating the query
                14. Always **use `CASE WHEN` or `COALESCE`** to handle potential NULL values in queries for columns.
                15. Maintain Table-Column Integrity: DO NOT CALL A COLUMN NAME WHICH BELONGS TO TABLE1 FROM TABLE2.
                        - VALID CALL : SELECT "short_company_name" FROM "master_prime_1d"
                        - INVALID CALL : SELECT "short_company_name" FROM "equity_prices_1d"
        STRICTILY DO NOT SELECT A COLUMN WHICH BELONGS TO SOME OTHER TABLE, MAKE SURE YOU MAINTAIN TABLE-COLUMN INTEGRITY           
        5. Ensure the query is optimized for ClickHouse version 24.12.1.850.
        Input:
        - Intent: [Brief summary of the query's goal]
        - Required Tables: [List of tables]
        - Columns: [List of columns needed]
        - Conditions: [List of conditions]
        - Joins: [Join requirements]
        - Aggregations: [Aggregations, if any]
        - Sorting/Grouping: [Details, if applicable]
        Output:
        - Generated SQL Query: [Executable SQL Query]

        Example:
        Input:
        - Intent: Retrieve the average closing price for IT industry stocks over the last 30 days.
        - Required Tables: `master_prime_1d`, `equity_prices_1d`
        - Columns: `close`, `industry_name`
        - Conditions: `industry_name = 'IT'`, `date_time BETWEEN '2024-11-01' AND '2024-11-30'`
        - Joins: `master_prime_1d.security_code = equity_prices_1d.security_code`
        - Aggregations: `avg(close)`
        - Sorting/Grouping: None

        Generated SQL Query:
        SELECT avg("close") AS average_closing_price
        FROM "equity_prices_1d"
        JOIN "master_prime_1d"
        ON "master_prime_1d"."security_code" = "equity_prices_1d"."security_code"
        WHERE "master_prime_1d"."industry_name" = 'IT'
        AND "equity_prices_1d"."date_time" BETWEEN '2024-11-01' AND '2024-11-30';
    

Generate an optimized query strictly adhering to ClickHouse syntax.

Strictily Adhere to the following instructions:
###OUTPUT SHOULD BE STRICTILY A SQL EXCUTABLE QUERY###
###DO NOT ADD COMMENTS TO THE QUERY###
###AVOID UNNECESSARY STEPS, REDUNDANT CALCULATIONS, OR EXTRANEOUS COMMENTS.###
###ENSURE THE QUERY ADHERES STRICTLY TO THE USER’S REQUIREMENTS WITHOUT ASSUMPTIONS OR ADDED CONTEXT.###
"""


    output_2 = generate_text(prompt2)
    prompt3=f"""
    You are a Senior Data Engineer with 30 years of experience in Indian stock market investments, I have an output and I want you to extract only SQL query from it and validate whether it works or not. Finally provide SQL query as output.
    output :'{output_2}'
    Based on the following DB schema and rules, validate it and provide only SQL executable output
    ### **Database Structure**

    #### **Table: `master_prime_1d`**
    - **`security_code`**: Unique identifier for securities (e.g., stocks, bonds).
    - **`company_name`**: Full legal company name (e.g., Reliance Power Limited).
    - **`short_company_name`**: Stock symbol (e.g., RPOWER).
    - **`industry_name`**: Industry (e.g., IT, Pharmaceuticals).
    - **`broad_industry_name`**: Broader category (e.g., Technology).
    - **`major_sector_name`**: Sector (e.g., Manufacturing).
    - **`index_name`**: Stock market index (e.g., Nifty 500).

    #### **Table: `equity_prices_1d`**
    - **`date_time`**: Trading day timestamp.
    - **`security_code`**: Security identifier.
    - **`open`**: Opening price.
    - **`high`**: Highest price.
    - **`low`**: Lowest price.
    - **`close`**: Closing price.
    - **`volume`**: Units traded.
    - **`version`**: Record version for integrity.
    STRICTILY DO NOT SELECT A COLUMN WHICH BELONGS TO SOME OTHER TABLE, STRICTILY MAKE SURE YOU MAINTAIN TABLE-COLUMN INTEGRITY

    ### **IMPORTANT INSTRUCTIONS**
    1. **Default Timeframe**: Use `{settings['timeframe']}` if the user does not specify a timeframe.  
    2. **Average Volume**: Default period is the last 20 days unless otherwise stated.  
    3. **Supported Timeframes**: Valid timeframes: {', '.join(SUPPORTED_TIMEFRAMES)}.  
    4. **Date Reference**: Use the current date ({current_date}) and calculate periods dynamically.  
    - **Valid format**: "2024-11-19"  
    - **Invalid format**: "2024-11-19 00:00:00"  
    5. **Dynamic Periods**: For terms like "last 1 month," use {settings['current_date_minus_1_month']} to {settings['current_date']}.  
    6. **Comparison Values**: Default to percentages unless absolute values are specified.  
    7. **`index_name` Check**: Use `LIKE` to verify values instead of direct equality checks.  
    8. **Stock Details**: Provide **`company_name`** only; do not include `security_code`.  
    9. **Distinct Names**: Use **`DISTINCT`** when selecting `company_name`.  
    10. **UNION Results**: Use **UNION ALL** (to include duplicates) or **UNION DISTINCT** (to exclude duplicates).  
    11. **Avoid Division Errors**: Use **`CASE WHEN`** or **`COALESCE`** to handle illegal divisions.  
    12. **LIKE Operator**: Apply only to string columns, not numeric fields like `security_code` or `volume`.  
    13. **Short Names**: Use `short_company_name` ('{short_company_name}') if required.  
    14. **Null Handling**: Use **`CASE WHEN`** or **`COALESCE`** for potential NULL values.  
    15. **Table-Column Integrity**:  
    - Valid: `SELECT "short_company_name" FROM "master_prime_1d"`  
    - Invalid: `SELECT "short_company_name" FROM "equity_prices_1d"`

    Strictily Adhere to the following instructions:
    ###OUTPUT SHOULD BE STRICTILY A SQL EXCUTABLE QUERY###
    ###DO NOT ADD COMMENTS TO THE QUERY###
    ###AVOID UNNECESSARY STEPS, REDUNDANT CALCULATIONS, OR EXTRANEOUS COMMENTS.###
    ###ENSURE THE QUERY ADHERES STRICTLY TO THE USER’S REQUIREMENTS WITHOUT ASSUMPTIONS OR ADDED CONTEXT.###

    """
    
    output=generate_text(prompt2)
    final_output = output
    k=0
    if  '```sql' in output:
        final_output = re.sub('sql', '', output, flags=re.IGNORECASE)
        final_output=re.sub('```','',final_output, flags=re.IGNORECASE)
        k=25
    if ';' in output[-1:]:
        final_output=final_output[:-1]
        k=25
    if '00:00:00' in final_output:
        final_output=re.sub(' 00:00:00', '',final_output)
        k=25
    if '12:00:00' in final_output:
        final_output=re.sub(' 12:00:00', '',final_output)
    if 'NSE' in final_output:
        final_output=re.sub('NSE','%%', final_output)
        k=25
    if k==0:    
        final_output=output
    #return output
    return [x_raw, output,final_output]

# DEFAULT_TIMEFRAME = "Daily"
# DEFAULT_AVG_VOLUME_PERIOD = "20-day"
# DEFAULT_NEAR_RANGE_PERCENT = 5
# settings = {
#     "timeframe": DEFAULT_TIMEFRAME,
#     "avg_volume_period": DEFAULT_AVG_VOLUME_PERIOD,
#     "near_range_percent": DEFAULT_NEAR_RANGE_PERCENT,
#     "current_date": current_date.strftime("%Y-%m-%d"),
#     "current_date_minus_1_month": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
#     "current_date_minus_1_week": (current_date - timedelta(days=7)).strftime("%Y-%m-%d"),
# }
# generate_sql_query("Which stocks on NSE showed the highest price increase in the last trading session?",settings)


