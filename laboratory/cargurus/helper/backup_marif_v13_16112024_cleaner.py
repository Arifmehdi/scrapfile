import csv
import re
import os
from datetime import datetime
import requests

def get_lat_long(zip_code=77007, api_key="4b84ff4ad9a74c79ad4a1a945a4e5be1", country_code="us"):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={zip_code},{country_code}&key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            geometry = data['results'][0]['geometry']
            latitude = geometry['lat']
            longitude = geometry['lng']
            city_name = data['results'][0]['components'].get('city', '')
            return latitude, longitude, city_name
        else:
            print("No results found for this ZIP code.")
    else:
        print(f"Error: {response.status_code}")
    return None, None, None

# Example zip_code
batch_no = 10

# Get the current date dynamically in 'YYYY-MM-DD' format
# date = datetime.now().strftime('%m%d%Y')
# creadet_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
date = datetime.now().strftime('%m%d%Y')
created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# File paths
input_csv = f"../public/db/housetom_265_inventory_info.csv"
output_csv = f"../public/db/{date}/{date}_output_file.csv"
duplicates_file = f"../public/db/{date}/{date}_duplicates.txt"

# Check if output files already exist; if so, skip processing
if os.path.exists(output_csv) and os.path.exists(duplicates_file):
    print(f"Output files already exist. Skipping processing.")
else:
    # Check if the directory exists; if not, create it
    output_dir = f"../public/db/{date}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory created: {output_dir}")
    else:
        print(f"Directory already exists: {output_dir}")

    # Check if the input file exists
    if not os.path.exists(input_csv):
        print(f"Input file does not exist: {input_csv}")
    else:
        # Global dictionary to store dealer names and assign unique dealer IDs
        dealer_id_map = {}
        dealer_id_counter = 1

        # Function to generate/get dealer ID
        def get_dealer_id(dealer_name):
            global dealer_id_counter  # Correct usage: use `global` for global variables
            if dealer_name not in dealer_id_map:
                dealer_id_map[dealer_name] = dealer_id_counter
                dealer_id_counter += 1
            return dealer_id_map[dealer_name]

        # To store the rows we've already seen (for duplicate checking)
        seen_rows = set()

        # Open the duplicate log file
        with open(duplicates_file, mode='w') as dup_file:
            # Read the CSV file, clean the price, and write to a new file
            with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)

                header = next(reader)
                writer.writerow(header)
                for row in reader:
                    # Get unique dealer ID based on dealer_name (row[0] assumed as dealer_name)
                    dealer_id = get_dealer_id(row[1])
                    row[0] = f"CG-{row[8]}{dealer_id}"

                    # Format the phone number, price, miles, and monthly payment
                    formatted_number = re.sub(r'\D', '', row[2])
                    row[2] = formatted_number

                    latitude, longitude, city_name = get_lat_long(row[8])
                    if latitude is not None and longitude is not None:
                        # Ensure row has enough columns for latitude, longitude, and city name
                        if len(row) < 45:
                            row += [''] * (45 - len(row))  # Add empty columns if necessary

                        # Assign latitude, longitude, and city name to columns 42, 43, and 44
                        row[42] = latitude
                        row[43] = longitude
                        row[44] = city_name
                        
                        print(f"Latitude: {latitude}, Longitude: {longitude}, City: {city_name}")

                    if row[13] == 'N/A':
                        row[13] = 0
                        
                    cleaned_price = re.sub(r'[\$,]', '', row[17])
                    row[17] = cleaned_price

                    cleaned_miles = re.sub(r'[\,mi]', '', row[18])
                    row[18] = cleaned_miles

                    try:
                        # Parse the date string in 'MM/DD/YYYY HH:MM' format
                        original_date = datetime.strptime(row[32], '%m/%d/%Y %H:%M')
                        
                        # Convert it to 'YYYY-MM-DD HH:MM:SS' format for MySQL
                        row[32] = original_date.strftime('%Y-%m-%d %H:%M:%S')

                    except ValueError:
                        print(f"Invalid date format in row {reader.line_num}: {row[32]}")
                        row[32] = '0000-00-00 00:00:00'

                    row[33] = batch_no   
                    cleaned_monthly_pay = re.sub(r'\D', '', row[35])
                    row[35] = cleaned_monthly_pay

                    if row[39] == 'All-Wheel Drive':
                        row[39] = 'AWD'
                    elif row[39] == 'Rear-Wheel Drive':
                        row[39] = 'RWD'
                    elif row[39] == 'Front-Wheel Drive':
                        row[39] = 'FWD'
                    elif row[39] == 'Four-Wheel Drive':
                        row[39] = '4WD'

                    # Convert row to a tuple for easy comparison and duplication check
                    row_tuple = tuple(row)

                    if row_tuple not in seen_rows:
                        seen_rows.add(row_tuple)
                        writer.writerow(row)  # Write non-duplicate rows to the output CSV
                    else:
                        # Write duplicate row to the duplicate log file
                        dup_file.write(','.join(row) + '\n')

        print(f"Prices have been cleaned, duplicates removed, and written to {output_csv}")
        print(f"Duplicates have been logged in {duplicates_file}")
