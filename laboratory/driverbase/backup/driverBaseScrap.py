import requests
from bs4 import BeautifulSoup
import sys
import re
import time 
import csv
import os
from datetime import datetime
import mysql.connector
from mysql_connector import get_mysql_connection


    # remote_image_url,local_directory,local_image_path
def download_image(remote_url, directory_location, local_image_path):

    # Replace whitespaces in single_title with underscores

    # Create the directory if it doesn't exist
    if not os.path.exists(directory_location):
        os.makedirs(directory_location)
        
    response = requests.get(remote_url)
    if response.status_code == 200:
        with open(local_image_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully to {local_image_path}")
    else:
        print(f"Failed to download image from {remote_url}. Status code: {response.status_code}")

############### read sitemap and check target email exist or not and result is true so go for next
base_url = "https://driverbase.com"
addition_url = "/inventory/search/"
# addition_url = "inventory/location/"
# location_url  = "sanfrancisco-ca"

# location_url  = "palo-pinto-tx/acura" ==15
# location_url  = "fort-worth-tx/acura" ==15
# location_url  = "palo-pinto-tx/acura/cl" ==1 
# location_url  = "austin-tx/acura"  ==15 
# location_url  = "weatherford-tx/acura" ==15
location_url  = "lewisville-tx/acura"  ##==15 done here



# location_url  = "houston-tx/acura"  ==15
# location_url  = "dallas-tx/acura"  ==15
# location_url  = "round-rock-tx/acura" ==15 
# location_url  = "katy-tx/acura"   ==15
# location_url  = "san-antonio-tx/acura" == 15
# location_url  = "aubrey-tx/acura" ==15
# location_url  = "laredo-tx/acura"  ==4
# location_url  = "shady-shores-tx/acura"


directory_location = location_url.replace('/','_').replace('-', '_')
inventory_location_obj = location_url.split('/')
inventory_location = inventory_location_obj[0]
inventory_make = inventory_location_obj[1]
targated_url  = base_url+addition_url+location_url

web = requests.get(targated_url)
soup = BeautifulSoup(web.content, 'html.parser')


listing_count = soup.find('strong', id= "listing_count").text

zip_input = soup.find('input', {'id': 'select_zip'})
zip_value = zip_input['value']

table = soup.find_all('tr', class_ ="inventory_row")

result_list = []
href_list = []

for tr in table:
    single_url = base_url+tr.a['href']
    href_list.append(single_url)

    single_img = tr.find('img')['data-original']


    single_title = tr.h2.text
    single_type = tr.find('span', class_="label label-default square").text
    single_price = tr.find('img', class_="price_field").parent.text

    cleaned_amount_str = single_price.replace('$', '').replace(',', '')
    amount_int = int(cleaned_amount_str)

    # Convert the Tag object to a string before using re.search
    tr_str = str(tr)
    # Extract the script content containing the mileage information
    mileage_script = re.search(r'<script>.*?document\.write\(\'(.*?)\'\);.*?</script>', tr_str, re.DOTALL)
    # Check if a match is found
    if mileage_script:
        # Extract the mileage value using a regex
        mileage_match = re.search(r'(\d{1,3}(,\d{3})*(\.\d+)?)\s*<small>Miles</small>', mileage_script.group(1))
        single_mileage = mileage_match.group(1) if mileage_match else None

    tr_soup = BeautifulSoup(tr_str, 'html.parser')
    # Extracting engine details, transmission, and mileage
    engine_details_element = tr_soup.find('img', {'alt': 'Vehicle engine icon'})
    engine_details = engine_details_element.parent.text

    transmission_details_element = tr_soup.find('img', {'alt': 'Vehicle transmission icon'})
    transmission_details = transmission_details_element.parent.text

    mileage_details_element = tr_soup.find('img', {'alt': 'Vehicle mileage icon'})
    mileage_details = mileage_details_element.parent.text

    dealer_details_element = tr_soup.find('span', {'class': 'glyphicon glyphicon-map-marker meta'})
    dealer_details = dealer_details_element.parent.text.strip()
    dealer_obj = dealer_details.split(', ')
    dealer_name_info = dealer_obj[0]

    dealer_city = dealer_obj[1]
    dealer_state = ' '.join(filter(None, dealer_obj[2].split())).split('(')[0]

    dealer_address = dealer_city+', '+dealer_state
    
    star_details_element = tr_soup.find_all('span', {'class': 'glyphicon glyphicon-star'})
    star_count = len(star_details_element)
    # print(dealer_city,dealer_state,dealer_address)
    # sys.exit()
    # Find the div with VIN and Stock information
    vin_element = tr_soup.find('div', string='VIN:')
    stock_element = tr_soup.find('div', string='Stock:')

    # Find the div containing VIN information
    vin_div = tr_soup.find('div', string=lambda text: text and 'VIN' in text)

    # Check if the VIN div is found before extracting the value
    if vin_div:
        vin_value = vin_div.find('small').get_text(strip=True)
        vin_info = vin_value.split(': ')[1]
        print(vin_info)
    else:
        print("VIN not found")

    # Find the div containing Stock information
    stock_div = tr_soup.find('div', string=lambda text: text and 'Stock' in text)

    # Check if the Stock div is found before extracting the value
    if stock_div:
        stock_value = stock_div.find('small').get_text(strip=True)
        stock_info = stock_value.split(': ')[1]
        print(stock_info)
    else:
        print("Stock not found")
    
    stay_days = tr_soup.find('div', id='dayslisted22044742')
    
    # Incrementing dealer ID counter
    dealer_id_counter = 0

    # Get the current date
    current_date = datetime.now()
    current_month_number = current_date.month
    current_day = current_date.day
    current_year = current_date.year % 100

    unique_id = int(f"{current_year:02d}{current_month_number:02d}{current_day:02d}{dealer_id_counter:02d}")

    replace_title_whitespace = single_title.replace(' ', '_').replace('/', '_')
    local_image_path = f"{directory_location}/{replace_title_whitespace + vin_info + stock_info}.jpg"
    download_image(single_img, directory_location, local_image_path)

    # Specify the CSV file path
    csv_file_path = directory_location+".csv"

    if os.path.exists(csv_file_path):
        # print(f"The file '{csv_file_path}' exists.")
        column_data = []

        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)

            # Assuming the first row contains headers and you want data from the second column (index 1)
            for row in reader:
                if len(row) > 1:  # Ensure the row has at least two columns
                    column_data.append(row[3])
        if dealer_name_info not in column_data:
            dealer_id_counter += 1
            unique_id = int(f"{current_year:02d}{current_month_number:02d}{current_day:02d}{dealer_id_counter:02d}")
        # Now, column_data contains the data from the second column of the CSV file
        else:
            unique_id = int(f"{current_year:02d}{current_month_number:02d}{current_day:02d}{dealer_id_counter:02d}")
    else:
        print(f"The file '{csv_file_path}' does not exist.")
            # Creating dealer ID
    # dealer_id = f"{unique_id:08d}"
    dealer_id = unique_id
    # sys.exit()
    # List to store data from column 1

    current_timestamp = datetime.timestamp(datetime.now())
    dt_object = datetime.fromtimestamp(current_timestamp)

    # Create a dictionary
    item_dict = {
        "dealer_id": dealer_id,
        "zip_code": zip_value,
        "city": inventory_location,
        "make": inventory_make,
        "dealer_name": dealer_name_info,
        "dealer_address": dealer_address,
        "dealer_city": dealer_city,
        "dealer_state": dealer_state,
        "details_url": single_url,
        "img_url": single_img,
        "local_img_url": local_image_path,
        "title": single_title,
        "type": single_type,
        "price": amount_int,
        "miles": single_mileage,
        "engine_details": engine_details,
        "transmission": transmission_details,
        "mileage": mileage_details,
        "vin": vin_info,
        "stock": stock_info,
        "star": star_count,
        'created_at' : dt_object,
    }
    result_list.append(item_dict)
    time.sleep(10)

    # Specify the CSV header
    csv_header = [
        'dealer_id',
        'zip_code',
        'city',
        'make',
        'dealer_name',
        'dealer_address',
        'dealer_city',
        'dealer_state',
        'details_url',
        'img_url',
        'local_img_url',
        'title',
        'type',
        'price',
        'miles',
        'engine_details',
        'transmission',
        'mileage',
        'vin',
        'stock',
        'star',
        'created_at'
    ]

    # print(result_list)
    # sys.exit()
    # Write the data to the CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_header)
        
        # Write the header
        writer.writeheader()
        writer.writerows(result_list)
        
        # for csv_inventory in result_list:
        #         # Write the data
        #     #   if  dealer_name_info not in result_list:
        #     #         # dealer_id = csv_inventory[0]+1
        #     # writer.writerows(csv_inventory)
            # writer.writerow(csv_inventory)
        
# Creating a MySQL connection
conn = get_mysql_connection()
cursor = conn.cursor()

# Check if the table exists, and if not, create it
table_name = 'tmp_inventories'  # Replace with your actual table name
cursor.execute(f"SHOW TABLES LIKE '{table_name}'")

if not cursor.fetchone():
    # Table does not exist, create it
    create_table_query = """
    CREATE TABLE {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        dealer_id INT,
        zip_code INT,
        city VARCHAR(255),
        make VARCHAR(255),
        dealer_name VARCHAR(255),
        dealer_address VARCHAR(255),
        dealer_city VARCHAR(255),
        dealer_state VARCHAR(255),
        details_url TEXT,
        img_url TEXT,
        local_img_url TEXT,
        title VARCHAR(255) NOT NULL,
        type VARCHAR(255),
        price INT,
        miles VARCHAR(255),
        engine_details TEXT,
        transmission VARCHAR(255),
        mileage VARCHAR(255),
        vin VARCHAR(255),
        stock VARCHAR(255),
        star INT,
        created_at DATETIME
    )
    """.format(table_name=table_name)

    cursor.execute(create_table_query)
    conn.commit()

# ... (your existing code)
print('Data inserting into Mysql ........')
# Writing data to MySQL
for item_dict in result_list:
    # Assuming 'your_table' is the name of your MySQL table
    

    query = """
    INSERT INTO `{table_name}`
    (dealer_id, zip_code,city, make, dealer_name, dealer_address, dealer_city, dealer_state, details_url, img_url,local_img_url, title,
    type, price, miles, engine_details, transmission, mileage, vin, stock, star, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """.format(table_name=table_name)

    values = (
        item_dict['dealer_id'], item_dict['zip_code'], item_dict['city'], item_dict['make'], item_dict['dealer_name'],
        item_dict['dealer_address'],item_dict['dealer_city'],item_dict['dealer_state'], item_dict['details_url'], item_dict['img_url'],item_dict['local_img_url'],
        item_dict['title'], item_dict['type'], item_dict['price'], item_dict['miles'],
        item_dict['engine_details'], item_dict['transmission'], item_dict['mileage'],
        item_dict['vin'], item_dict['stock'], item_dict['star'], item_dict['created_at']
    )

    cursor.execute(query, values)

    # Optional: Pause between each insertion
    time.sleep(10)

# Committing the changes and closing the database connection
conn.commit()
cursor.close()
conn.close()

print('Data inserted into MySQL successfully')
sys.exit()
# print(engine_details,transmission_details,mileage_details,dealer_name_info,dealer_address_info, star_count,current_month_number,current_day,dealer_id,tr_soup, stay_days)

# with open(f"test03.txt", "w", encoding="utf-8") as file:
#         file.write(str(result_list))

# print(href_list)
# sys.exit()

print(soup)