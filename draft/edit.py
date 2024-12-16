import pandas as pd

df=pd.read_csv(r'C:\Users\Zelar\Documents\Strike_GPT\Pie25\output\3.5_Turbo\12-12\3.5_2.01.csv', encoding='latin5')

# Drop a column (replace 'column_name' with the name of the column to remove)
df = df.drop(columns=['result'])

# Optionally, save the DataFrame back to a CSV (if needed)
df.to_csv(r'C:\Users\Zelar\Documents\Strike_GPT\Pie25\output\3.5_Turbo\12-12\3.5_2.01.csv', index=False)