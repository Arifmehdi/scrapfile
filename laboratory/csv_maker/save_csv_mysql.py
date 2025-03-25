import pandas as pd
import mysql.connector
import numpy as np

# MySQL connection details
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "carbazar"
}

# Establish MySQL connection
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Read CSV file
# csv_file = "detail_20000_backup_raw.csv"
csv_file = "car_detail_2025_03_10_171715.csv"
df = pd.read_csv(csv_file)

# Column mapping (CSV header -> MySQL column)
column_mapping = {
    # "Customer ID": "customer_id",
    "Customer ID": "dealer_id",
    "Dealer Type": "dealer_type",
    "Dealer Name": "dealer_name",
    "Dealer Address": "dealer_address",
    "Dealer street": "dealer_street",
    "Dealer City": "dealer_city",
    "Dealer Region": "dealer_region",
    "Dealer Zip Code": "dealer_zip_code",
    "Dealer Sales Phone": "dealer_sales_phone",
    "Dealer Rating": "dealer_rating",
    "Dealer Review": "dealer_review",
    "Dealer Website": "dealer_website",
    "Brand Website": "brand_website",
    "Seller Note": "seller_note",
    "Source_url": "source_url",
    "Titles": "titles",
    "Trim Name": "trim_name",
    "Make": "make",
    "Model": "model",
    "Exterior Color": "exterior_color",
    "Interior Color": "interior_color",
    "Price": "price",
    "Mileage": "mileage",
    "Fuel": "fuel",
    "City Mpg": "city_mpg",
    "Hwy Mpg": "hwy_mpg",
    "Engine": "engine",
    "Transmission": "transmission",
    "Year": "year",
    "Type": "type",
    "Stock Number": "stock_number",
    "Vin": "vin",
    "Body Type": "body_type",
    "Feature": "feature",
    "Option": "options",
    "Drive Train": "drive_train",
    "Price History": "price_history",
    "Price Rating": "price_rating",
    "Primary Image": "primary_image",
    "All Image": "all_image",
    "Vin Image": "vin_image"
}

# Convert NaN values to None
df.replace({np.nan: None}, inplace=True)

# Get the max batch_no from the database
cursor.execute("SELECT MAX(batch_no) FROM csv_tmp_inventories")
max_batch_no = cursor.fetchone()[0]

# If no batch exists, start from 100, else increment by 1
batch_no = max_batch_no + 1 if max_batch_no else 100

# Add batch_no and status columns
columns = ", ".join(list(column_mapping.values()) + ["batch_no", "status"])
placeholders = ", ".join(["%s"] * (len(column_mapping) + 2))
insert_query = f"INSERT IGNORE INTO csv_tmp_inventories ({columns}) VALUES ({placeholders})"

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

print(f"Data inserted successfully (Batch No: {batch_no}, Status: 0, Duplicates Ignored)!")
