import os
import json
from API_keys.gemini_API import generate_text
# from API_keys.openai_API_API import generate_text
# from API_keys.perplexity_API_API import generate_text
# from API_keys.cohere_API import generate_text

def load_company_symbols(json_file):
    with open(json_file, "r") as file:
        return json.load(file)

def generate_sql_query(user_query, company_map):

    prompt = f"""
You are a Senior Data engineer who is expert in SQL and who also is investing in stock market for the past 30 years. Your task is to convert any natural language query about stock market data into a valid SQL query.

Each company has a table named after its ID, and all tables share the same columns:
- date
- opening_price
- closing_price
- highest_price
- lowest_price
- adjacent_close
- volume

Here is the company mapping for table names:
{company_map}

Given a user's question, identify:
1. The company's name and map it to the table name using the above dictionary.
2. The requested parameter (e.g., lowest_price, highest_price).

Instructions while generating SQL query:
1. STRICITLY provide only executable SQL query
2. DO NOT ADD any REDUNDANCY steps in the process
3. DO NOT ADD CONCLUSIONS, SUMMAMRY, NOTES at the END of PROCESS 
4. DO NOT USE SINGLE COLONS OR DOUBLE COLONS TO THE TABLE NAME
5. DO NOT ADD ```sql AT THE START AND ``` AT THE END OF THE OUTPUT

User Query: "{user_query}"
SQL Query:
"""

    return generate_text(prompt)

def validate_company(user_query, company_map):
    for company_name in company_map.keys():
        if company_name.lower() in user_query.lower():
            return company_name
    return None

if __name__ == "__main__":

    json_file = "C&S.json"
    company_map = load_company_symbols(json_file)

    print("Welcome to the Chatbot!")
    print('Enter your queries. Type "thank_you" to end the chat.\n')

    while True:
        user_query = input("Your Question: ").strip()

        if user_query.lower() == "thank_you":
            print("Thank you for using the Stock Market Chatbot. Goodbye!")
            break

        valid_company = validate_company(user_query, company_map)
        if not valid_company:
            print("Not a valid company. Proceeding with general query.\n")

        sql_query = generate_sql_query(user_query, company_map)
        print("\n")
        print(sql_query)
