# import pandas as pd

# # Load the tables with encoding handlin
# table1_path = r"C:\Users\Zelar\Documents\data dump\equity_prices_1d.csv"
# table2_path = r"C:\Users\Zelar\Documents\data dump\master_prime_1d.csv" 

# # Load files with appropriate encoding to avoid Unicode errors
# table1 = pd.read_csv(table1_path, encoding='latin1')  # 'latin1' handles a wider range of encodings
# table2 = pd.read_csv(table2_path, encoding='latin1')

# # Strip whitespace and normalize column names to lowercase for consistency
# table1.columns = table1.columns.str.strip().str.lower()
# table2.columns = table2.columns.str.strip().str.lower()

# # Ensure the 'security_code' column exists in both tables
# if 'security_code' not in table1.columns or 'security_code' not in table2.columns:
#     print("Column 'security_code' not found in one or both tables.")
# else:
#     # Convert date_time to datetime in table1
#     table1['date_time'] = pd.to_datetime(table1['date_time'], errors='coerce')

#     # Sort table1 by date_time
#     table1.sort_values(by='date_time', inplace=True)

#     # Merge the tables on 'security_code' with a left join
#     merged_data = pd.merge(table1, table2, on='security_code', how='left')

#     # Forward-fill company information for each 'security_code'
#     merged_data[['company_name', 'short_company_name', 'industry_name',
#                  'broad_industry_name', 'major_sector_name', 'index_name']] = (
#         merged_data.groupby('security_code')[['company_name', 'short_company_name', 'industry_name',
#                                               'broad_industry_name', 'major_sector_name', 'index_name']]
#         .fillna(method='ffill')
#     )

#     # Sort the merged data by date_time and security_code
#     merged_data.sort_values(by=['date_time', 'security_code'], inplace=True)

#     # Display the merged DataFrame (for testing purposes)
#     print("Merged and Sorted DataFrame:")
#     print(merged_data.head())

#     # Save to a new CSV file
#     merged_data.to_csv("denormalized_sorted_output.csv", index=False, encoding='utf-8')

# import pandas as pd

# # File paths
# table1_path = r"C:\Users\Zelar\Documents\data dump\equity_prices_1d.csv"
# table2_path = r"C:\Users\Zelar\Documents\data dump\master_prime_1d.csv"

# # Load table2 with optimized data types
# table2 = pd.read_csv(table2_path, encoding='latin1')
# table2.columns = table2.columns.str.strip().str.lower()

# # Optimize data types for table2
# categorical_cols = ['security_code', 'company_name', 'short_company_name', 'industry_name',
#                     'broad_industry_name', 'major_sector_name', 'index_name']
# for col in categorical_cols:
#     if col in table2.columns:
#         table2[col] = table2[col].astype('category')

# # Process table1 in chunks
# chunk_size = 50000  # Adjust chunk size as needed
# merged_chunks = []

# # Read and process table1 in chunks
# for chunk in pd.read_csv(table1_path, encoding='latin1', chunksize=chunk_size):
#     # Normalize column names
#     chunk.columns = chunk.columns.str.strip().str.lower()

#     # Ensure 'security_code' exists
#     if 'security_code' not in chunk.columns:
#         raise KeyError("Column 'security_code' not found in table1.")

#     # Convert 'date_time' to datetime format
#     if 'date_time' in chunk.columns:
#         chunk['date_time'] = pd.to_datetime(chunk['date_time'], errors='coerce')

#     # Sort chunk by 'date_time'
#     chunk.sort_values(by='date_time', inplace=True)

#     # Merge the current chunk with table2
#     merged_chunk = pd.merge(chunk, table2, on='security_code', how='left')

#     # Forward-fill missing values for company information
#     fill_cols = ['company_name', 'short_company_name', 'industry_name',
#                  'broad_industry_name', 'major_sector_name', 'index_name']
#     for col in fill_cols:
#         if col in merged_chunk.columns:
#             merged_chunk[col] = merged_chunk.groupby('security_code')[col].fillna(method='ffill')

#     # Append processed chunk to the list
#     merged_chunks.append(merged_chunk)

# # Combine all processed chunks
# merged_data = pd.concat(merged_chunks, ignore_index=True)

# # Final sort by 'date_time' and 'security_code'
# if 'date_time' in merged_data.columns:
#     merged_data.sort_values(by=['date_time', 'security_code'], inplace=True)

# # Save the merged DataFrame to a CSV file
# output_path = r"denormalized_sorted_output.csv"
# merged_data.to_csv(output_path, index=False, encoding='utf-8')

# print(f"Merged and sorted data saved to {output_path}.")
import pandas as pd
from tqdm import tqdm

table1_dtypes = {
    'security_code': 'category',
    'open': 'float32',
    'high': 'float32',
    'low': 'float32',
    'close': 'float32',
    'volume': 'int32',
    'version': 'int32',
}

table2_dtypes = {
    'security_code': 'category',
    'company_name': 'category',
    'short_company_name': 'category',
    'industry_name': 'category',
    'broad_industry_name': 'category',
    'major_sector_name': 'category',
    'index_name': 'category',
}

table2 = pd.read_csv(r"C:\Users\Zelar\Documents\data dump\master_prime_1d.csv", encoding='latin1', dtype=table2_dtypes)
table2.set_index('security_code', inplace=True)

chunk_size = 500000
chunks = pd.read_csv(r"C:\Users\Zelar\Documents\data dump\equity_prices_1d.csv", encoding='latin1', dtype=table1_dtypes, parse_dates=['date_time'], chunksize=chunk_size)

output_file = "denormalized_sorted_output_tab.csv"
first_chunk = True

with open(output_file, 'w', encoding='utf-8') as f:
    for chunk in tqdm(chunks, desc="Processing chunks"):
        # Set index for merging
        chunk.set_index('security_code', inplace=True)

        # Merge with Table 2
        merged_chunk = chunk.join(table2, how='left').reset_index()

        # Write to CSV
        if first_chunk:
            merged_chunk.to_csv(f, index=False, header=True)
            first_chunk = False
        else:
            merged_chunk.to_csv(f, index=False, header=False, mode='a')