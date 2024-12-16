import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from shot2_1 import generate_sql_query
from pql_click_hit import DatabaseConnector
import os
import time
from rapidfuzz import fuzz, process
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Initialize database connector
db_connector = DatabaseConnector()

# Current date settings
current_date = datetime.strptime("2024-11-19", "%Y-%m-%d")
settings = {
    "timeframe": "Daily",
    "avg_volume_period": "20-day",
    "near_range_percent": 5,
    "current_date": current_date.strftime("%Y-%m-%d"),
    "current_date_minus_1_month": (current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
    "current_date_minus_1_week": (current_date - timedelta(days=7)).strftime("%Y-%m-%d"),
}

# Configurable directory for saving query results
results_dir = r"./user_results"  # Change this to your desired directory
os.makedirs(results_dir, exist_ok=True)  # Ensure directory exists

# Initialize session state for query and results
if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""
if "query_result" not in st.session_state:
    st.session_state["query_result"] = None

# Streamlit app
st.title("SQL Query and Feedback App")

# User query input
user_query = st.text_area("Enter your query:", value=st.session_state["user_query"])

# Button to execute query
if st.button("Execute Query"):
    if user_query.strip():
        st.session_state["user_query"] = user_query  # Save query in session state
        try:
            sql_query = generate_sql_query(user_query, settings)
            try:
                query_result = db_connector.hit_sql(sql_query["Final SQL"])  # Execute SQL query
                st.session_state["query_result"] = query_result  # Save result in session state
                st.success("Query executed successfully!")
                if isinstance(query_result, pd.DataFrame):
                    st.write("Query Result:")
                    st.dataframe(query_result)  # Display the result
                else:
                    st.write("Query Result:", query_result)
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
        except Exception as e:
            st.error(f"Error generating SQL: {str(e)}")
    else:
        st.warning("Please enter a query.")

# Button to save query results
if st.session_state["query_result"] is not None:
    if st.button("Save Query Results"):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        file_path = os.path.join(results_dir, f"query_result_{timestamp}.csv")
        if isinstance(st.session_state["query_result"], pd.DataFrame):
            st.session_state["query_result"].to_csv(file_path, index=False)
        else:
            with open(file_path, "w") as file:
                file.write(str(st.session_state["query_result"]))
        st.success(f"Query result saved to {file_path}")

# Feedback form
st.subheader("Feedback Form")
user_name = st.text_input("User Name:")
question = st.text_area("Question:", value=st.session_state["user_query"], disabled=True)
answer = st.text_area("Answer:", value=str(st.session_state["query_result"]), disabled=True)
pass_flag = st.radio("Pass:", options=[True, False])
comments = st.text_area("Comments:")

# Button to submit feedback
if st.button("Submit Feedback"):
    if user_name.strip():
        try:
            # Insert feedback into ClickHouse
            db_connector.hit_sql(
                """
                INSERT INTO feedback_table (id, updated_at, updated_at_date, user_name, question, answer, pass, comments)
                VALUES (%(id)s, now(), today(), %(user_name)s, %(question)s, %(answer)s, %(pass)s, %(comments)s)
                """,
                {
                    "id": int(time.time()),  # Use timestamp as unique ID
                    "user_name": user_name,
                    "question": question,
                    "answer": answer,
                    "pass": pass_flag,
                    "comments": comments,
                },
            )
            st.success("Feedback submitted successfully!")
        except Exception as e:
            st.error(f"Error submitting feedback: {str(e)}")
    else:
        st.warning("Please enter your name before submitting feedback.")

# Fuzzy matching functions
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

def get_short_company_name(user_query, company_data, threshold=69):
    matched_company_name, matched_short_name = fuzzy_substring_match(user_query, company_data, threshold)
    return matched_short_name if matched_short_name else None

# Example usage of fuzzy matching
company_data = pd.read_csv(r"C:\Users\Zelar\Documents\Strike_GPT\Pie25\data\company_maps.csv")
short_name = get_short_company_name(user_query, company_data)
if short_name:
    st.write(f"Matched Company Symbol: {short_name}")
