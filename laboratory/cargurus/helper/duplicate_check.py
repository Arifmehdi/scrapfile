import pandas as pd


df = pd.read_csv('custom_all.csv')
print("Columns in CSV:", df.columns)

column_name = 'Vin'
df_cleaned = df.drop_duplicates(subset=[column_name], keep='first')
df_cleaned.to_csv('custom_all02.csv', index=False)

print("Duplicates removed, and file saved successfully.")




## another way 
## -----------------
# import pandas as pd

# # Load the CSV file
# df = pd.read_csv('custom_all.csv')

# # Check for duplicate VINs in column Q
# duplicates = df[df.duplicated(subset=['Vin'], keep=False)]

# # Print duplicate VINs
# print(duplicates)