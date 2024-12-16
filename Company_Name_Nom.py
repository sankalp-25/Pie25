import pandas as pd
from rapidfuzz import fuzz, process

# Load the company data
company_data = pd.read_csv(r"C:\Users\Zelar\Documents\Strike_GPT\Pie25\data\company_maps.csv")

def fuzzy_substring_match(query, company_data, threshold=75):
    try:
        best_match = process.extractOne(query, company_data['company_name'], scorer=fuzz.partial_ratio)
        if best_match and best_match[1] >= threshold:
            matched_company = best_match[0]
            row = company_data.loc[
                company_data['company_name'].str.lower().str.strip() == matched_company.lower().strip()
            ]
            if not row.empty:
                return matched_company, row.iloc[0]['symbol']
    except Exception as e:
        print(f"Error during fuzzy match: {e}")
    return None, None

def get_short_company_name(user_query):
    matched_company_name, matched_short_name = fuzzy_substring_match(user_query, company_data, threshold=69)
    return matched_short_name if matched_short_name else None
