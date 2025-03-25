import pandas as pd
import mysql.connector
import numpy as np

# MySQL connection details
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "dbc"
}

# Establish MySQL connection
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Read CSV file
# csv_file = "location_data.csv"
csv_file = "state_zip_tax_county_short_code_2.csv"
df = pd.read_csv(csv_file)

# Column mapping (CSV header -> MySQL column)
column_mapping = {
    "Source Url": "src_url",
    "City": "city",
    "Zip code": "zip_code",
    "County": "county",
    "State": "state",
    "Short Name": "short_name",
    "Country": "country",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Combibe tax": "combine_tax",
}

# Convert NaN values to None
df.replace({np.nan: None}, inplace=True)

# Get the max batch_no from the database
cursor.execute("SELECT MAX(batch_no) FROM csv_location_zips")
max_batch_no = cursor.fetchone()[0]

# If no batch exists, start from 100, else increment by 1
batch_no = max_batch_no + 1 if max_batch_no else 100

# Add batch_no and status columns
columns = ", ".join(list(column_mapping.values()) + ["batch_no", "import_status"])
placeholders = ", ".join(["%s"] * (len(column_mapping) + 2))
insert_query = f"INSERT INTO csv_location_zips ({columns}) VALUES ({placeholders})"  # Removed IGNORE

# Insert each row with batch_no and status = 0
for _, row in df.iterrows():
    values = [row[col] if col in df.columns else None for col in column_mapping.keys()]
    values.append(batch_no)  # Add batch_no
    values.append(0)  # Set status = 0
    cursor.execute(insert_query, values)

# Commit and close connection
connection.commit()
cursor.close()
connection.close()

print(f"Location data inserted successfully (Batch No: {batch_no}, Status: 0)!")
