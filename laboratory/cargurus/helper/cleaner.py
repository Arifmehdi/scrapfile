import csv
import re
import os
from datetime import datetime

# Example zip_code
zip_code = 77007

# Get the current date dynamically in 'YYYY-MM-DD' format
date = datetime.now().strftime('%m%d%Y')

# File paths
# input_csv = f"../public/db/{zip_code}/{date}/inventory_info.csv"
input_csv = f"../public/db/77007-houseton/inventory_info.csv"
output_csv = f"../public/db/{zip_code}_{date}/{zip_code}_{date}_output_file2.csv"
duplicates_file = f"../public/db/{zip_code}_{date}/{zip_code}_{date}_duplicates2.txt"

# Check if output files already exist; if so, skip processing
if os.path.exists(output_csv) and os.path.exists(duplicates_file):
    print(f"Output files already exist. Skipping processing.")
else:
    # Check if the directory exists; if not, create it
    output_dir = f"../public/db/{zip_code}_{date}"
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
            global dealer_id_counter  # Make dealer_id_counter global to modify it
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
                    row[0] = f"CG-{zip_code}{dealer_id}"

                    # Format the phone number, price, miles, and monthly payment
                    formatted_number = re.sub(r'\D', '', row[2])
                    row[2] = formatted_number

                    if row[13] == 'N/A':
                        row[13] = 0
                        
                    cleaned_price = re.sub(r'[\$,]', '', row[17])
                    row[17] = cleaned_price

                    cleaned_miles = re.sub(r'[\,mi]', '', row[18])
                    row[18] = cleaned_miles

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
