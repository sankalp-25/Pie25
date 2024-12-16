import os
import json
import google.generativeai as venky

# os.environ["API_KEY"] = "YOUR_API_KEY"
# genai.configure(api_key=os.environ["API_KEY"])

venky.configure(api_key="AIzaSyCyyMZhbQ1TDtaOCIOaT_wdV8b621IBTTE")

def load_company_symbols(json_file):

    with open(json_file, "r") as file:
        return json.load(file)

def generate_sql_query(user_query, company_map):
    # Prompt for Gemini
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
4. DO NOT USE SINGLE COLONS OR DOUBLE COLONS FOR THE TABLE NAME
5. DO NOT ADD ```sql AT THE START AND ``` AT THE END OF THE OUTPUT

User Query: "{user_query}"
SQL Query:
"""

    # Use Gemini to generate the SQL query
    model = venky.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Return only the SQL query from the response
    print(response.text)
    return response.text

def validate_company(user_query, company_map):
    for company_name in company_map.keys():
        if company_name.lower() in user_query.lower():
            return company_name
    return None

if __name__ == "__main__":
    # Load company symbols from JSON
    json_file = "C&S.json"  # Replace with the path to your JSON file
    company_map = load_company_symbols(json_file)

    print("Welcome to the Chatbot!")
    print('Enter your queries. Type "thank_you" to end the chat.\n')

    while True:
        # Take input from the user
        user_query = input("Your Question: ").strip()

        # End the chat if the user types "thank_you"
        if user_query.lower() == "thank_you":
            print("Thank you for using the Stock Market Chatbot. Goodbye!")
            break

        # Validate the company in the query
        valid_company = validate_company(user_query, company_map)
        if not valid_company:
            print("Not a valid company. Please enter a valid company.\n")
            continue

        # Generate SQL query
        sql_query = generate_sql_query(user_query, company_map)
        # print(sql_query)