import os
import json
import re
import time
from datetime import datetime, timedelta, date
from API_keys.gemini_API import generate_text
#from API_keys.openai_API import generate_text
#from API_keys.perplexity_API import generate_text
#from API_keys.cohere_API import generate_text
#from API_keys.mistral_API import generate_text
from Company_Name_Nom import get_short_company_name

SUPPORTED_TIMEFRAMES = [
    "5min", "15min", "30min", "45min", "75min", "120min", "240min", "125min",
    "Hourly", "Daily", "Weekly", "Monthly", "Quarterly"
]

table_schema = {
    "master_prime_1d": {"security_code", "company_name", "short_company_name", "industry_name", 
                        "broad_industry_name", "major_sector_name", "index_name"},
    "equity_prices_1d": {"date_time", "security_code", "open", "high", "low", "close", "volume", "version"}
}
current_date = datetime.strptime("2024-11-19", "%Y-%m-%d")


def preprocess_query(user_query):
    """Preprocess user query using prompt1."""
    short_company_name = get_short_company_name(user_query)
    prompt1 = fprompt1 = f"""
    You are an expert data analyst specializing in stock market data. Preprocess the following query:

    Query: {user_query}

    Instructions:
    1. Extract intent, required tables, columns, conditions, joins, aggregations, and sorting/grouping.
    2. Validate that all columns strictly belong to the specified tables in the schema.
    3. If a column does not exist in the schema, exclude it and adjust the components accordingly.
    4. Output in structured format with the intent and components.

    Schema:
    - `master_prime_1d`: {["security_code", "company_name", "short_company_name", "industry_name", "broad_industry_name", "major_sector_name", "index_name"]}
    - `equity_prices_1d`: {["date_time", "security_code", "open", "high", "low", "close", "volume", "version"]}
    """

    response = generate_text(prompt1)
    response_cleaned = re.sub('NSE', '', response, flags=re.IGNORECASE)
    return response_cleaned


def generate_sql(preprocessed_output, user_query, settings):
    """Generate SQL query using prompt2."""
    prompt2 = fprompt2 = f"""
    You are a Senior Data Engineer. Convert the following structured query components into a valid SQL query.

    Components: {preprocessed_output}
    User Query: {user_query}

    Database Schema:
    - Tables: master_prime_1d, equity_prices_1d.
        #### **Table: `master_prime_1d`**
        - **Columns**: security_code, company_name, short_company_name, industry_name, broad_industry_name, major_sector_name, index_name.
        #### **Table: `equity_prices_1d`**
        - **Columns**: date_time, security_code, open, high, low, close, volume, version.

    Instructions:
    1. Generate a ClickHouse-compatible SQL query.
    2. Only use columns strictly from their respective tables.
    3. Ensure table-column mappings strictly adhere to the schema. For example:
    - `security_code` is present in both tables but must be joined explicitly.
    - Financial columns like `open`, `close`, and `volume` are **only** in `equity_prices_1d`.
    - Descriptive columns like `company_name` are **only** in `master_prime_1d`.
    4. Follow these settings:
    - Timeframe: {settings['timeframe']}
    - Current Date: {current_date}.
    5. Optimize the query for ClickHouse compatibility without adding extraneous assumptions.

    Output: Provide only the SQL query.
    """

    sql_query = generate_text(prompt2)
    return sql_query


def validate_sql(sql_query):
    """Validate and clean the SQL query using prompt3."""
    prompt3 = fprompt3 = f"""
    Validate the following SQL query for correctness and adherence to the schema:

    Query: {sql_query}

    Rules:
    1. Strictly verify table-column mapping based on this schema:
    - `master_prime_1d`: {["security_code", "company_name", "short_company_name", "industry_name", "broad_industry_name", "major_sector_name", "index_name"]}
    - `equity_prices_1d`: {["date_time", "security_code", "open", "high", "low", "close", "volume", "version"]}
    2. If any column references are incorrect, correct them.
    3. Ensure proper table joins where columns span multiple tables.
    4. ###OUTPUT SHOULD BE STRICTILY A SQL EXCUTABLE QUERY###
    5. ###DO NOT ADD COMMENTS TO THE QUERY###
    6. ###AVOID UNNECESSARY STEPS, REDUNDANT CALCULATIONS, OR EXTRANEOUS COMMENTS.###
    7. ###ENSURE THE QUERY ADHERES STRICTLY TO THE USER’S REQUIREMENTS WITHOUT ASSUMPTIONS OR ADDED CONTEXT.###

    """

    validated_query = generate_text(prompt3)
    time.sleep(2)
    return clean_sql(validated_query)


def clean_sql(sql_query):
    """
    Clean and validate the SQL query. If invalid column integrity is found, trigger validate_sql().
    
    Args:
    - sql_query (str): The SQL query to clean and validate.
    - user_query (str): The original user query for context.
    - table_schema (dict): The database schema mapping table names to their respective columns.
    
    Returns:
    - str: The cleaned and validated SQL query.
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)

    def log_debug_info(step, content):
        logging.debug(f"{step}: {content}")

    # Clean up common artifacts
    if '```sql' or '```' in sql_query:
        sql_query = re.sub(r'```sql|```', '', sql_query, flags=re.IGNORECASE)
    if '00:00:00' or '12:00:00' in sql_query:
        sql_query = re.sub(r'\s+00:00:00|\s+12:00:00', '', sql_query)

    # Validate column integrity
    for table, columns in table_schema.items():
        for match in re.findall(rf"{table}\.(\w+)", sql_query):
            if match not in columns:
                error_message = f"""
                    {sql_query}
                    IMPORTANT NOTE:
                    The query is not correct, it is not following column integrity since `{match}` doesn't belong to `{table}`; based on the original user query and table schema, provide the correct SQL query.
                    """
                
                log_debug_info("Column Integrity Error", error_message)
                return validate_sql(error_message)

    # If no issues, return the cleaned query
    return sql_query.strip()

def generate_sql_query(user_query, settings):
    """Main function to preprocess, generate, and validate SQL query."""
    preprocessed_output = preprocess_query(user_query)
    time.sleep(2)
    raw_sql = generate_sql(preprocessed_output, user_query, settings)
    time.sleep(2)
    final_sql = validate_sql(raw_sql)
    time.sleep(2)
    return {
        "Preprocessed": preprocessed_output,
        "Raw SQL": raw_sql,
        "Final SQL": final_sql
    }
