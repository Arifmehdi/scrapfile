import csv

# Input and output CSV file paths
input_csv = 'input_file.csv'
output_csv = 'output_file.csv'

# Function to clean the price
def clean_price(price):
    return price.replace('$', '').replace(',', '').strip()

# Read the CSV file, clean the price, and write to a new file
with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        # Assuming the price is in the first column, change the index accordingly
        row[0] = clean_price(row[0])
        writer.writerow(row)

print(f"Prices have been cleaned and written to {output_csv}")