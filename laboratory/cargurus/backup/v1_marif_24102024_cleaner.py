import csv
import re



# Input and output CSV file paths
# zip_code  = 77007 
zip_code  = 75241 
# input_csv = f"../public/db/{zip_code}/inventory_info.csv"
# output_csv = f"../public/db/{zip_code}/{zip_code}_output_file.csv"
input_csv = f"../public/db/2/inventory_info.csv"
output_csv = f"../public/db/2/2_output_file.csv"

# Function to clean the price
def clean_price(price):
    return price.replace('$', '').replace(',', '').strip()

# Read the CSV file, clean the price, and write to a new file
with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        formatted_number = re.sub(r'\D', '', row[2])
        row[2] = formatted_number
        
        cleaned_price = re.sub(r'[\$,]', '', row[17])
        row[17] = cleaned_price

        cleaned_miles = re.sub(r'[\,mi]', '', row[18])
        row[18] = cleaned_miles

        cleaned_monthly_pay = re.sub(r'\D', '', row[35])
        row[35] = cleaned_monthly_pay


        dealer_id = get_dealer_id( row[0])

        print(formatted_number)
        print(cleaned_price)
        print(cleaned_miles)
        print(cleaned_monthly_pay)
 

        
        # Assuming the price is in the first column, change the index accordingly
        # row[0] = clean_price(row[0])
        writer.writerow(row)

print(f"Prices have been cleaned and written to {output_csv}")