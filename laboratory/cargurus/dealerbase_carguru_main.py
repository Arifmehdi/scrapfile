from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import requests
import sqlite3
import hashlib
import os
import time
import csv
import logging
import sys

import re
# from mysql_connector import get_mysql_connection


# def setup_db_and_csv():
#     # Prepare SQLite3 connection and create tables if they don't exist
#     conn = sqlite3.connect('driverbase.db')
#     cursor = conn.cursor()

#     # Create vehicles table
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS vehicles (
#         vehicle_name TEXT,
#         status TEXT,
#         price TEXT,
#         vin TEXT,
#         stock TEXT,
#         mpg_city TEXT,
#         mpg_highway TEXT,
#         engine TEXT,
#         transmission TEXT,
#         dealer_id INTEGER,
#         days_on_driverbase TEXT,
#         views TEXT,
#         image_url TEXT,
#         custom_link TEXT,
#         detail_price TEXT,
#         detail_status TEXT,
#         detail_engine TEXT,
#         local_image_path TEXT,
#         downloaded_image_paths TEXT,
#         FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
#     )
#     ''')

#     # Create dealers table
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS dealers (
#         dealer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         dealer_href TEXT,
#         dealer_text TEXT,
#         detail_dealer_phone TEXT
#     )
#     ''')

#     # Prepare CSV files only if they don't already exist
#     vehicle_csv_file = 'vehicle_data.csv'
#     dealer_csv_file = 'dealer_data.csv'

#     vehicle_csv_headers = ['Vehicle', 'Status', 'Price', 'VIN', 'Stock', 'MPG City', 'MPG Highway', 'Engine', 
#                            'Transmission', 'Dealer ID', 'Days on Driverbase', 'Views', 'Image URL', 'Custom Link', 
#                            'Detail Price', 'Detail Status', 'Detail Engine', 'Single Local Image', 'Detail 5 Local Images']

#     dealer_csv_headers = ['Dealer ID', 'Dealer Link', 'Dealer Text', 'Detail Dealer Phone']

#     if not os.path.exists(vehicle_csv_file):
#         with open(vehicle_csv_file, mode='w', newline='', encoding='utf-8') as file:
#             writer = csv.writer(file)
#             writer.writerow(vehicle_csv_headers)  # Write headers once
#             logging.info(f"CSV file '{vehicle_csv_file}' created and headers written.")
#     else:
#         logging.info(f"CSV file '{vehicle_csv_file}' already exists. Skipping CSV creation.")

#     if not os.path.exists(dealer_csv_file):
#         with open(dealer_csv_file, mode='w', newline='', encoding='utf-8') as file:
#             writer = csv.writer(file)
#             writer.writerow(dealer_csv_headers)  # Write headers once
#             logging.info(f"CSV file '{dealer_csv_file}' created and headers written.")
#     else:
#         logging.info(f"CSV file '{dealer_csv_file}' already exists. Skipping CSV creation.")

#     return conn, cursor, vehicle_csv_file, dealer_csv_file

def setup_db_and_csv():
    # Connect to SQLite database (creates a new database if it doesn't exist)
    file_path = "public/db/"
    db_name = "carguru_data.db"
    db = file_path+db_name

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    else:
        logging.info(f"{file_path} already exists. No file created.")
    

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Create tables for dealers, inventories, and inventory details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dealers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dealer_id TEXT,
            name TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            dealer_full_address TEXT,
            dealer_iframe_map TEXT,
            zip TEXT,
            about_me TEXT,
            img TEXT,
            radius TEXT,
            rating TEXT,
            review_count_only TEXT,
            inventory_link TEXT
        )
    ''')

    # ### *** step 01             FOREIGN KEY(dealer_id) REFERENCES dealers(id),  inventory_link, single_img, 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            inventory_link TEXT,
            single_img TEXT,
            dealer_name TEXT,
            dealer_address TEXT,
            status_text TEXT,
            title TEXT,
            mileage TEXT,
            engine TEXT,
            price TEXT,
            payment TEXT,
            deal_rating TEXT,
            description TEXT,
            phone TEXT,
            location TEXT
        )
    ''')

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS inventory_details (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         inventory_id INTEGER,
    #         detail_key TEXT,
    #         detail_value TEXT,
    #         FOREIGN KEY(inventory_id) REFERENCES inventories(id)
    #     )
    # ''')

    conn.commit()

    # Create CSV files and writers for dealers, inventories, and inventory details
    dealer_csv_file = open('public/db/dealers_info.csv', mode='a', newline='', encoding='utf-8')
    # # new comment 01
    inventory_csv_file = open('public/db/inventory_info.csv', mode='a', newline='', encoding='utf-8')

    ### *** step 02
    # inventory_details_csv_file = open('inventory_details.csv', mode='a', newline='', encoding='utf-8')

    dealer_csv_writer = csv.writer(dealer_csv_file)
    # # new comment 02
    inventory_csv_writer = csv.writer(inventory_csv_file)

    ### *** step 03
    # inventory_details_csv_writer = csv.writer(inventory_details_csv_file)

    # Write headers if files are empty
    if os.stat('public/db/dealers_info.csv').st_size == 0:
        dealer_csv_writer.writerow(['Dealer ID', 'Dealer Name', 'Phone', 'Address', 'City', 'State', 'Custom Address' , 
                                    'Dealer Iframe Map', 'Zip Code','About Dealer', 'Dealer Image','Radius', 'Rating','Review Count', 'Invnetory Link'])

    # # new comment 03
    if os.stat('public/db/inventory_info.csv').st_size == 0:
        inventory_csv_writer.writerow(['Inventory Link', 'Single Image Link', 'Vehicle ID', 'Dealer Name', 'Dealer Address', 'Status', 'Title', 'Mileage', 'Engine', 'Price', 'Payment', 
                                        'Rating', 'Dealer Description', 'Phone', 'Location'])

    ### *** step 04
    # if os.stat('inventory_details.csv').st_size == 0:
    #     inventory_details_csv_writer.writerow(['Inventory ID', 'Detail Key', 'Detail Value'])

    return conn, cursor, dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer
    return conn, cursor, dealer_csv_file, dealer_csv_writer



# Function to check if a dealer exists in the SQLite database
def get_existing_dealer_id(cursor, name, full_address, zip_code):
    cursor.execute('''
        SELECT dealer_id FROM dealers 
        WHERE name = ? AND dealer_full_address = ? AND zip = ?
    ''', (name, full_address, zip_code))
    result = cursor.fetchone()
    return result[0] if result else None

# Function to generate a new dealer ID
def get_new_dealer_id(cursor):
    cursor.execute('''
        SELECT dealer_id FROM dealers ORDER BY dealer_id DESC LIMIT 1
    ''')
    last_id = cursor.fetchone()
    if last_id:
        # Increment the numeric part of the last dealer ID
        last_id_number = int(last_id[0].split('-')[1])
        return f"D-{last_id_number + 1}"
    else:
        return "D-24770071"  # Start from this ID if no dealers exist

def store_data_in_csv_and_sqlite(vehicle_data, dealer_data, cursor, conn, vehicle_csv_file, dealer_csv_file):
    # Unpack vehicle and dealer data
    (vehicle_name, status, price, vin, stock, mpg_city, mpg_highway, engine, transmission, dealer_id,
     days_on_driverbase, views, image_src, cus_link, detail_price, detail_status, detail_engine, 
     local_image_path, downloaded_image_paths) = vehicle_data

    (dealer_href, dealer_text, detail_dealer_phone) = dealer_data

    # Store dealer data in SQLite3 (first check if the dealer exists)
    cursor.execute('''
        INSERT INTO dealers (dealer_href, dealer_text, detail_dealer_phone)
        VALUES (?, ?, ?)
    ''', (dealer_href, dealer_text, detail_dealer_phone))
    dealer_id = cursor.lastrowid  # Get the auto-incremented dealer ID
    conn.commit()

    # Store vehicle data in SQLite3
    cursor.execute('''
        INSERT INTO vehicles (
            vehicle_name, status, price, vin, stock, mpg_city, mpg_highway, engine, transmission,
            dealer_id, days_on_driverbase, views, image_url, custom_link, detail_price, detail_status, 
            detail_engine, local_image_path, downloaded_image_paths
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (vehicle_name, status, price, vin, stock, mpg_city, mpg_highway, engine, transmission, dealer_id,
          days_on_driverbase, views, image_src, cus_link, detail_price, detail_status, detail_engine, 
          local_image_path, downloaded_image_paths))
    conn.commit()

    # Store dealer data in CSV
    with open(dealer_csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([dealer_id, dealer_href, dealer_text, detail_dealer_phone])  # Append dealer data

    # Store vehicle data in CSV
    with open(vehicle_csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([vehicle_name, status, price, vin, stock, mpg_city, mpg_highway, engine, transmission, 
                         dealer_id, days_on_driverbase, views, image_src, cus_link, detail_price, detail_status, 
                         detail_engine, local_image_path, downloaded_image_paths])  # Append vehicle data
        

def initialize_webdriver():
    logging.info("Initializing WebDriver")
    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        sys.exit(1)

def custom_url():
    
    base_url = "https://www.cargurus.com/Cars/mobile/requestZipForDealersNearMe.action"
    # addition_url = f"dealers/map?search.Zip={zip_code}&search.DistanceFromZip={zip_radius}"
    # targated_url  = base_url+addition_url

    return base_url


def get_page_content_hash(driver):
    """Generate a hash of the current page's content to detect duplicates."""
    page_content = driver.page_source
    return hashlib.md5(page_content.encode('utf-8')).hexdigest()


def navigate_to_next_page(driver, page_number):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="srp-desktop-page-navigation-next-page"]'))
        )
        next_button.click()
        logging.info(f"Navigating to page {page_number + 2}")
        
        # Wait for the new page to load
        WebDriverWait(driver, 10).until(
            EC.staleness_of(next_button)
        )


        time.sleep(5)  # Additional sleep to ensure the new content is fully loaded
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False
    return True



def scroll_down_slowly(driver, scroll_pause_time=0.5, step=300):
    """
    Scrolls down the page slowly.

    :param driver: Selenium WebDriver instance
    :param scroll_pause_time: Time to pause between scrolls (seconds)
    :param step: The amount of pixels to scroll down with each step
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down by 'step' pixels
        driver.execute_script(f"window.scrollBy(0, {step});")

        # Wait for the page to load new content or for animation
        time.sleep(scroll_pause_time)

        # Check the current scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # If we've reached the bottom, break
        if new_height == last_height:
            break

        last_height = new_height



def count_svg_stars(item):
    svgs = item.find_all('svg', {'data-testid': 'star-full'})
    return len(svgs)



def download_image(remote_url, directory_location, local_image_path):                                   # remote_image_url,local_directory,local_image_path
    time.sleep(3)

    if os.path.exists(local_image_path):                                                                # Check if the file already exists
        print(f"Image already exists at {local_image_path}, skipping download.")
        return                                                                                          # Skip downloading the image if it exists

    if not os.path.exists(directory_location):                                                           # Create the directory if it doesn't exist
        os.makedirs(directory_location)
        
    response = requests.get(remote_url)
    if response.status_code == 200:
        with open(local_image_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully to {local_image_path}")
    else:
        print(f"Failed to download image from {remote_url}. Status code: {response.status_code}")



def scrape_detail_page(driver, vehicle_data, single_vehicle_data, link):
    # Open a new tab with the link
    driver.execute_script("window.open(arguments[0], '_blank');", link)
    time.sleep(2)  # Wait for the tab to open
    
    # Get the current window handles
    windows = driver.window_handles
    
    try:
        # Ensure there's a new window to switch to
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])  # Switch to the new tab

            # Wait for the detailed page to load
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@id='cargurus-listing-search']")))

            # Scraping logic (as before)
            detail_title = driver.find_element(By.XPATH, "//h1[@data-cg-ft='vdp-listing-title']").text if driver.find_elements(By.XPATH, "//h1[@data-cg-ft='vdp-listing-title']") else 'No title'
            detail_price = driver.find_element(By.XPATH, "//h2[@class='us1dS CrxtQ']").text if driver.find_elements(By.XPATH, "//h2[@class='us1dS CrxtQ']") else 'No price'
            detail_address_city_state = driver.find_element(By.XPATH, "//p[@class='us1dS iK3Zj']").text if driver.find_elements(By.XPATH, "//p[@class='us1dS iK3Zj']") else 'No address'

            detail_dealer_review = driver.find_element(By.XPATH, "//button[@class='JRPjD _8KIJA QXloi LCpwg7']").text if driver.find_elements(By.XPATH, "//button[@class='JRPjD _8KIJA QXloi LCpwg7']") else 'No review'
            detail_dealer_telephone = driver.find_element(By.XPATH, "//span[@class='RTKKej']").text if driver.find_elements(By.XPATH, "//span[@class='RTKKej']") else 'No telephone'

            # Scrape all images
            detail_dealer_images_elements = driver.find_elements(By.XPATH, "//div[@class='RENFam']//button//img")
            detail_dealer_images = [img.get_attribute('src') for img in detail_dealer_images_elements] if detail_dealer_images_elements else ['No Images']

            detail_dealer_images_elements = driver.find_element(By.XPATH, "//div[@class='dKPlkE']")
            html_content = detail_dealer_images_elements.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            file_path = 'public/cargurus_vehicle_detail_html.txt'


            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(soup.prettify())
                logging.info(f"HTML content saved to {file_path}")
            else:
                logging.info(f"{file_path} already exists. No file created.")


                # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all sections and h2 headings
            sections = soup.find_all('section')

            # Initialize storage for the extracted data
            extracted_data = []

            for section in sections:
                section_data = {}
                
                # Get the h2 heading, or set as 'N/A' if missing
                h2 = section.find('h2')
                section_heading = h2.text.strip() if h2 else 'N/A'
                section_data['heading'] = section_heading

                # Special case for "Options" and "History"
                if section_heading == 'Options' or section_heading.startswith('History'):
                    ul = section.find('ul')
                    if ul:
                        options = [item.text.strip() for item in ul.find_all('p')]
                        section_data['items'] = ', '.join(options) if options else 'N/A'
                    else:
                        section_data['items'] = 'N/A'
                # Special case for "Pricing"
                elif section_heading == 'Pricing':
                    ul = section.find('ul')
                    if ul:
                        pricing_info = [item.text.strip() for item in ul.find_all('p')]
                        section_data['items'] = ', '.join(pricing_info) if pricing_info else 'N/A'
                    else:
                        section_data['items'] = 'N/A'
                # Special case for "Safety" (handling SVG stars)
                elif section_heading == 'Safety':
                    ul = section.find('ul')
                    if ul:
                        section_data['items'] = []
                        list_items = ul.find_all('li')
                        for item in list_items:
                            key = item.find('span', class_='gUBXY5')
                            rating = count_svg_stars(item)
                            key_text = key.text.strip() if key else 'N/A'
                            section_data['items'].append(f"{key_text}: {rating}")
                else:
                    # Handle other sections with typical key-value pairs
                    ul = section.find('ul')
                    if ul:
                        section_data['items'] = []
                        list_items = ul.find_all('li')
                        
                        for item in list_items:
                            key_value = {}
                            
                            # Find the key, often in a <h5> or <span> (use 'N/A' if missing)
                            key = item.find('h5') or item.find('span', class_='gUBXY5')
                            key_text = key.text.strip() if key else 'N/A'
                            
                            # Find the value, often in a <p> or <span> (use 'N/A' if missing)
                            value = item.find('p') or item.find('span', class_='eqBXWZ')
                            value_text = value.text.strip() if value else 'N/A'
                            
                            # Append to the section data
                            section_data['items'].append(f"{key_text}: {value_text}")
                
                # Append the section data to the main list if it contains data
                if section_data:
                    extracted_data.append(section_data)

                detail_dealer_images_elements = driver.find_element(By.XPATH, "//section[@class='TRQLFd']")
                # 

            # Display the extracted data
            for data in extracted_data:
                print(f"Section: {data['heading']}")
                if 'items' in data:
                    if isinstance(data['items'], list):
                        for item in data['items']:
                            print(f" - {item}")
                    else:
                        # For sections like Options, History, Pricing, display in one line
                        print(f" - {data['items']}")
                print()

            # for section in sections:
            #     section_data = {}
                
            #     # Get the h2 heading, or set as 'N/A' if missing
            #     h2 = section.find('h2')
            #     section_data['heading'] = h2.text.strip() if h2 else 'N/A'

            #     # Get all list items (li) within the section
            #     ul = section.find('ul')
            #     if ul:
            #         list_items = ul.find_all('li')
            #         section_data['items'] = []
                    
            #         for item in list_items:
            #             key_value = {}
                        
            #             # Find the key, often in a <h5> or <span> (use 'N/A' if missing)
            #             key = item.find('h5') or item.find('span', class_='gUBXY5')
            #             key_value['key'] = key.text.strip() if key else 'N/A'
                        
            #             # Find the value, often in a <p> or <span> (use 'N/A' if missing)
            #             value = item.find('p') or item.find('span', class_='eqBXWZ')
            #             key_value['value'] = value.text.strip() if value else 'N/A'
                        
            #             # Append to the section data
            #             section_data['items'].append(key_value)
                
            #     # Append the section data to the main list if it contains data
            #     if section_data:
            #         extracted_data.append(section_data)

            # # Display the extracted data
            # for data in extracted_data:
            #     print(f"Section: {data['heading']}")
            #     if 'items' in data:
            #         for item in data['items']:
            #             print(f" - {item['key']}: {item['value']}")
            #     print()

            # Print the scraped data
            print("Title:", detail_title)
            print("Price:", detail_price)
            print("Address:", detail_address_city_state)
            print("Dealer Review:", detail_dealer_review)
            print("Dealer Telephone:", detail_dealer_telephone)
            print("Dealer Images:", detail_dealer_images)

            time.sleep(5)  # Pause for a while if needed

        else:
            print("Failed to open new tab.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the new tab if it exists and switch back to the original window
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[1])  # Switch back to the first tab

# def scrape_detail_page(driver, vehicle_data, single_vehicle_data,link):
#     """
#     Scrapes detailed page for a single vehicle entry.
#     """
        
#     # main_url = single_vehicle_data['Main Url']
#     # base_url = single_vehicle_data['Base Url']

#      # Click the link to open the details page
#     driver.execute_script("window.open(arguments[0], '_blank');", link)
#     driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab


#     # return driver,main_url,base_url, replace_title_whitespace, vin_info, stock_info 
#     # Wait for the detail page to load and scrape data (add your detailed page scraping logic here)
#     try:
#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@id='detail_vehicle_data']")))
#         # Add your scraping logic here for the detailed page

#         # Example: Scrape more data from the detailed page
#         detail_title = driver.find_element(By.XPATH, "//h1[@data-cg-ft='vdp-listing-title']").text  if detail_title else 'No title'
#         detail_price = driver.find_element(By.XPATH, "//h2[@class='us1dS CrxtQ']").text  if detail_price else 'No price'
#         detail_address_city_state = driver.find_element(By.XPATH, "//p[@class='us1dS iK3Zj']").text  if detail_address_city_state else 'No address'
#         # detail_monthly_pay = driver.find_element(By.XPATH, "//span[@id='pmt']").text  

#         detail_status_span = driver.find_elements(By.XPATH, "//span[@class='QOdmp OjhRM']").text if detail_status_span else 'No status'
#         # detail_possible_statuses = ["New", "Preowned", "Certified Preowned"]
#         # detail_status = "Not Found"
#         # detail_engine = "Not Found"
#         # for detail_span in detail_status_span:
#         #     detail_span_text = detail_span.text.strip()
#         #     if detail_span_text in detail_possible_statuses:
#         #         detail_status = detail_span_text

#         #         parent_element = detail_span.find_element(By.XPATH, '..')
#         #         parent_text = parent_element.text.strip()
#         #         detail_engine = parent_text.replace(detail_status, '').strip()
#         #         break
            

#         detail_dealer_review = driver.find_element(By.XPATH, "//button[@class='JRPjD _8KIJA QXloi LCpwg7']").text if detail_dealer_review else 'No review'
#         detail_dealer_telephone = driver.find_element(By.XPATH, "//span[@class='RTKKej']").text if detail_dealer_telephone else 'No telephone'
#         detail_dealer_images = driver.find_elements(By.XPATH, "//div[@class='RENFam']//button//img").get_attribute('src') if detail_dealer_images else 'No Images'

#         print(detail_title)
#         print(detail_price)
#         print(detail_address_city_state)
#         print(detail_status_span)
#         print(detail_dealer_review)
#         print(detail_dealer_telephone)
#         print(detail_dealer_images)
#         time.sleep(5)
#         return
#         sys.exit()

#         detail_dealer_link_tag = driver.find_element(By.XPATH, "//a[contains(@href, '/dealers/id/')]")

#         detail_dealer_href =  detail_dealer_link_tag.get_attribute('href') if detail_dealer_link_tag else "Dealer link not found"
#         detail_dealer_text = detail_dealer_link_tag.text.strip() if detail_dealer_link_tag else "Dealer text not found"
#         detail_dealer_phone = driver.find_element(By.XPATH, "//header//div//div[2]//div[2]//div[3]//div//a[1]//button//span[2]").text  

#         # --- Scraping for "Number of days on driverbase" ---
#         detail_days_text = driver.find_element(By.XPATH, "//span[starts-with(@id,'dayslisted')]").text

#         # --- Scraping for "glyphicon-eye-open" views ---
#         detail_views_span = driver.find_element(By.XPATH, "//span[contains(@class, 'glyphicon-eye-open')]")
#         detail_views_text = detail_views_span.find_element(By.XPATH, "following-sibling::small").text.strip() if detail_views_span else "Views not found"

#         detail_rows = driver.find_elements(By.XPATH,'//table[@id="sort"]//tbody//tr')

#         vehicle_details = {}
#         for row in detail_rows:
#             key_element = row.find_element(By.XPATH, './td[1]')  # First <td> is the key
#             value_element = row.find_element(By.XPATH, './td[2]')  # Second <td> is the value
#             # Extract the text from the elements
#             key = key_element.text.strip().replace(":", "")  # Remove the colon from the key
#             value = value_element.text.strip()
#             # Add the key-value pair to the dictionary
#             vehicle_details[key] = value
        
        
#         try:
#             detail_dealer_web_link = driver.find_element(By.XPATH, '//span[@class="col-xs-6 meta"]//a').get_attribute('href')
#         except Exception as e:
#             print(f"Error fetching dealer web link: {e}")
        
#         # --- Scraping for "glyphicon-map-marker" (dealer name) ---
#         try:
#             # Locate the element by class name
#             detail_dealer_name = driver.find_element(By.CLASS_NAME, 'glyphicon-map-marker')
#             dealer_button = detail_dealer_name.find_element(By.XPATH, 'following-sibling::button')
#             detail_dealer_name_text = dealer_button.text.strip()
#         except Exception as e:
#             detail_dealer_name_text = "Dealer Name not found"
#         # --- Scraping for "glyphicon-map-marker" (dealer name) ---

#         try:
#             # Locate the element by class name
#             detail_dealer_comment = driver.find_element(By.XPATH, '//header//div//div[2]/div[5]/span').text.strip()
#         except Exception as e:
#             detail_dealer_comment = "Dealer Comment not found"
        
#         replace_title_whitespace = detail_title.replace(' ', '_').replace('/', '_').replace('-', '_')
#         # vin_info = single_vehicle_data['VIN']
#         # stock_info = single_vehicle_data['Stock']
#         vin_info = vehicle_details['VIN #']
#         stock_info = vehicle_details['Stock #']
#         print(replace_title_whitespace)
#         print(vin_info)
#         print(stock_info)
#         try:
#             replace_title_whitespace = detail_title.replace(' ', '_').replace('/', '_').replace('-', '_')
#             # vin_info = single_vehicle_data['VIN']
#             # stock_info = single_vehicle_data['Stock']
#             vin_info = vehicle_details['VIN #'].replace(' [check for recalls]','')
#             stock_info = vehicle_details['Stock #']

#             img_stack = driver.find_element(By.XPATH, '//img[@src="/public/img/icn/img-stack.png"]')
#             img_stack_src = img_stack.get_attribute('src')
#             print(f"Image stack src: {img_stack_src}")
#             sibling_images = img_stack.find_elements(By.XPATH, '../../following-sibling::div//img')
#             sibling_image_sources = [img.get_attribute('src') for img in sibling_images]
#             image_sources_str = ",".join(sibling_image_sources)

#             # Print all sibling image sources found
#             downloaded_image_paths = []
#             for idx, img_src in enumerate(sibling_image_sources[:5], 1):
#                 print(f"Attempting to download image {idx} from {img_src}") 
#                 location_url = main_url.split('/')[-1]
#                 directory_location = 'uploads/'+location_url.replace('/','_').replace('-', '_')+'/'+vin_info
#                 detail_local_image_path = f"{directory_location}/{replace_title_whitespace + '_' + vin_info + '_' + stock_info}_{idx}.jpg" 
#                 download_image(img_src, directory_location, detail_local_image_path)
#                 downloaded_image_paths.append(detail_local_image_path)
#                 print(f"Sibling image {idx} src: {img_src}")

#         except Exception as e:
#             print(f"Error fetching images: {e}")

#         # Print the extracted details
#         for key, value in vehicle_details.items():
#             print(f"{key}: {value}")

#         detail_vehicle_info = []

#         detail_monthly_pay = 'N/A'
#         detail_info = {
#             'detail_title' : detail_title,
#             'detail_price' : detail_price,
#             'detail_status' : detail_status_span,
#             # 'detail_engine' : detail_engine,
#             'detail_monthly_pay' : detail_monthly_pay,
#             'detail_monthly_pay' : detail_address_city_state,
#             'detail_dealer_href' : detail_dealer_href,
#             'detail_dealer_name' : detail_dealer_text,
#             'detail_dealer_phone' : detail_dealer_phone,
#             'detail_days_text' : detail_days_text,
#             'detail_views_text' : detail_views_text,
#             'detail_dealer_web_link' : detail_dealer_web_link,
#             'detail_dealer_name_text' : detail_dealer_name_text,

#             'detail_dealer_comment' : detail_dealer_comment,
#             'downloaded_image_paths' : downloaded_image_paths,

#         }
#         detail_vehicle_info.append(detail_info)
#         detail_vehicle_info.append(vehicle_details)
#         time.sleep(3)

#     except Exception as e:
#         print(f"Error fetching details from the page: {e}")
    
#     # # Close the detail tab and switch back to the main window
#     # driver.close()
#     # driver.switch_to.window(driver.window_handles[0])

#     window_handles = driver.window_handles

#         # Close the last (third) tab
#     driver.switch_to.window(window_handles[2])  # Switch to the last tab
#     driver.close()  # Close the last tab

#     # Switch to the second tab
#     driver.switch_to.window(window_handles[1])
#     return detail_vehicle_info
        
def extract_vehicle_info(URL, driver, conn, cursor, csv_writers, all_data, header_data):
# def extract_vehicle_info(URL, driver, all_data, header_data):
    inventories_count = 0 
    if URL:
        base_url = "https://www.cargurus.com"
        target_url = base_url + URL
        driver.execute_script("window.open(arguments[0], '_blank');", target_url)
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab

    try:
        # while True:  # Loop through pages
            data = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//main[@id="main"]'))
            )
            dealer_name = data.find_element(By.XPATH,'//div[@class="dealerDetailsHeader"]//h1').text
            dealer_address = data.find_element(By.XPATH,'//div[@class="dealerDetailsInfo"]').text

            inventory_obj = data.find_element(By.XPATH,'//div[@class="fzhq3E"]')
            html_content = inventory_obj.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            file_path = 'public/cargurus_single_html.txt'
            print(f"single page : {dealer_name}")
            print(f"single page : {dealer_address}")

            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(soup.prettify())
                logging.info(f"HTML content saved to {file_path}")
            else:
                logging.info(f"{file_path} already exists. No file created.")

            rows = soup.find_all('div', class_='pazLTN')
            for row in rows:
                # print(row)
                try:

                    # Extracting a tag href
                    a_elem = row.find('a', {'data-testid': 'car-blade-link'})
                    a_href = a_elem['href'] if a_elem else "N/A"
                    print(f'Link Href : {a_href}')
                    # Extracting image src
                    img_elem = row.find('img', {'data-cg-ft': 'srp-listing-blade-image'})
                    single_img_src = img_elem['src'] if img_elem else "N/A"
                    print(f'Image Source : {single_img_src}')
    
                    status = row.find('span', {'data-eyebrow': True})
                    status_text = status.text.strip() if status else "N/A"
                    print(f'loop 01 : {status_text}')

                    # title_elem = row.find('h4', class_='gN7yGT')
                    # title = title_elem.text.strip() if title_elem else "N/A"
                    # print(f'loop 02 : {title}')

                    # Find title
                    title_elem = row.find('h4', {'data-cg-ft': 'srp-listing-blade-title'})
                    title = title_elem.text.strip() if title_elem else "N/A"
                    print(f'loop 02 : {title}')

                    mileage_elem = row.find('p', {'data-testid': 'srp-tile-mileage'})
                    mileage = mileage_elem.text.strip() if mileage_elem else "N/A"
                    print(f'loop 03 : {mileage}')

                    engine_elem = row.find('p', {'data-testid': 'seo-srp-tile-engine-display-name'})
                    engine = engine_elem.text.strip() if engine_elem else "N/A"
                    print(f'loop 04 : {engine}')

                    price_elem = row.find('h4', {'data-testid': 'srp-tile-price'})
                    price = price_elem.text.strip() if price_elem else "N/A"
                    print(f'loop 05 : {price}')

                    # payment_elem = row.find('span', class_='R1T5Pw')
                    # payment = payment_elem.text.strip() if payment_elem else "N/A"
                    # print(f'loop 06 : {payment}')

                    # Find payment
                    payment_elem = row.find('span', class_='_monthlyPaymentText_noan4_230')
                    payment = payment_elem.text.strip() if payment_elem else "N/A"
                    print(f'loop 06 : {payment}')

                    deal_rating_elem = row.find('span', class_='QOdmp')
                    deal_rating = deal_rating_elem.text.strip() if deal_rating_elem else "N/A"
                    print(f'loop 07 : {deal_rating}')

                    # description_elem = row.find('div', {'data-testid': 'srp-tile-options-list'})
                    # description = description_elem.text.strip() if description_elem else "N/A"
                    # print(f'loop 08 : {description}')

                    # Find dealer description
                    description_elem = row.find('div', class_='_text_1ncld_1')
                    description = description_elem.text.strip() if description_elem else "N/A"
                    print(f'loop 08 : {description}')

                    phone_elem = row.find('button', {'data-testid': 'button-phone-number'})
                    phone = phone_elem.text.strip() if phone_elem else "N/A"
                    print(f'loop 09 : {phone}')

                    location_elem = row.find('div', {'data-testid': 'srp-tile-bucket-text'})
                    location = location_elem.text.strip() if location_elem else "N/A"
                    print(f'loop 10 : {location}')

                    cus_inventory_link = target_url + a_href
                    
                    result = {
                        'Inventory Link ' : cus_inventory_link,
                        'Single Image' : single_img_src,
                        'Dealer Name' : dealer_name,
                        'Dealer Addres' : dealer_address,
                        'Status' : status_text,
                        'Title' : title,
                        'Mileage' : mileage,
                        'Engine' : engine,
                        'Price' : price,
                        'Payment' : payment,
                        'Deal Rating' : deal_rating,
                        'Description' : description,
                        'Phone' : phone,
                        'Location' : location
                    }
                    # Print the formatted output
                    print(result)
                    print("="*50)
                    # Scroll down the page
                    scroll_down_slowly(driver)
                    detail_vehicle_data = []
                    scrape_detail_page(driver, detail_vehicle_data, result,cus_inventory_link)
                    time.sleep(5)
                except AttributeError:
                    # Skip the row if any field is missing
                    # continue
                    print("Not to mind now !")

                vehicle_id = 'C-241000'
                # Insert into SQLite
                cursor.execute('''
                    INSERT INTO vehicles (inventory_link, single_img, vehicle_id, dealer_name, dealer_address, status_text, title, mileage, engine, price, payment, 
                                            deal_rating, description, phone, location
                                        )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?)
                ''', (a_href, single_img_src, vehicle_id, dealer_name, dealer_address, status_text, title, mileage, engine, price, payment, 
                        deal_rating, description, phone, location
                    ))
                conn.commit()

                # dealer_id = cursor.lastrowid 

#                 # Write to dealers CSV
                csv_writers[3].writerow([a_href, single_img_src, vehicle_id, dealer_name, dealer_address, status_text, title, mileage,
                                        engine, price, payment, deal_rating, description, phone, location])

#                 # Append the single vehicle's data to all_data
#                 # single_all_data.append(single_vehicle_data)

#                 detail_vehicle_data =[]
#                 # infor = scrape_detail_page(driver, detail_vehicle_data, single_vehicle_data, link)
                
                # print(infor)
                # print('*'*40)
                
            number_of_pages = 3
            print(number_of_pages)
            for page in range(number_of_pages - 1):
                print(page)
                if not navigate_to_next_page(driver, page):
                    break
                extract_vehicle_info(None, driver, conn, cursor, csv_writers, all_data, header_data)

            return dealer_name, dealer_address

    except Exception as e:
        logging.error(f"Error occurred while extracting vehicle information: {e}")

    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return dealer_name, dealer_address


# def extract_dealer_info(URL, driver, conn, cursor, csv_writers, all_data, header_data):
def extract_dealer_info(driver, conn, cursor, dealer_csv_writer,single_all_data, HEADER):
    try:
        single_driver = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//section[@class="results"]'))
        )
    except AttributeError as e :
        logging.error("Timeout waiting for page to load: %s", e)
        single_driver.quit()
        sys.exit(1)

    inventories_count = 0 

    single_header = single_driver.find_element(By.XPATH,'//div[@class="headerSort"]//h1').text
    single_dealer_num = single_driver.find_element(By.XPATH,'//span[@class="searchDescription"]').text

    html_content = single_driver.get_attribute('innerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')
    file_path = 'public/cargurus_html.txt'

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

        logging.info(f"HTML content saved to {file_path}")
    else:
        logging.info(f"{file_path} already exists. No file created.")

    # single_all_data = []
    # dealer_datas  = single_driver.find_elements(By.XPATH,'//div[@class="blade"]')
    base_url = 'https://www.cargurus.com'
    dealerships = soup.find_all('div', class_='blade')
    for dealer in dealerships:
        name = dealer.find('strong').text.strip()
        inventory_link = dealer.find('a', class_='viewInventory')['href']
        inventory_link_cus = base_url+inventory_link

        address = dealer.find('div', class_='address').text.strip()          # Split the address into parts based on newline and commas
        address_parts = address.split('\n')
        actual_address = address_parts[0].strip()               # Get the full address without the radius part
        address_details = actual_address.split(',')             # Split the actual address by commas
        city = address_details[-2].strip()                  # Extract the city, state, and zip from the last two parts # Always the second to last part
        state_zip = address_details[-1].strip().split()  # The last part contains state and zip
        state = state_zip[0]  # State (e.g., 'TX')
        zip_code = state_zip[1]  # Zip code (e.g., '78237')
        full_address = ', '.join(address_details[:-2]).strip()  # The address before city

        # Check if dealer already exists
        existing_dealer_id = get_existing_dealer_id(cursor, name, full_address, zip_code)
        if existing_dealer_id:
            dealer_id = existing_dealer_id  # Use existing dealer ID
        else:
            dealer_id = get_new_dealer_id(cursor)  # Generate a new unique dealer ID
        # Combine everything before the city as the full address (including any suite numbers if present)


        # Extract the radius, if it exists
        radius = address_parts[1].strip() if len(address_parts) > 1 else None
        radius = radius.replace("(", "").replace(")", "") if radius else None

        # If there is a distance, extract it
        radius = address_parts[1].strip() if len(address_parts) > 1 else None
        radius = radius.replace("(", "").replace(")", "") if radius else None

        dealer_data = []
        single_name, single_address = extract_vehicle_info(inventory_link, driver, conn, cursor, dealer_csv_writer, dealer_data, HEADER)


        rating_element = dealer.find('div', class_='dealerRating')
        if rating_element:
            rating = rating_element.find('strong', class_='averageOverallRating').text.strip()
        else:
            rating = "N/A"


        if rating_element:
            reviews_count = rating_element.text.strip().replace(' ','').replace(' Shopper reviews','')

            cleaned_reviews_count = reviews_count.strip()
            match = re.search(r'\((\d+)\)', cleaned_reviews_count)
            if match:
                review_count_only = match.group(1)  # Get the first captured group (the number)

        else:
            review_count_only = "N/A"

        
        review_element = dealer.find('blockquote')
        if review_element:
            review_text = review_element.text.strip()
        else:
            review_text = "No reviews available"

        img_wrapper = dealer.find('div', class_='imgWrapper')
        if img_wrapper:
            img_element = img_wrapper.find('img')
            img_src = img_element['src'] if img_element else "No image"
        else:
            img_src = "No image"

        address_cus = f"{city +', '+ state}" 

        dealer_iframe_map = 'N/A'
        phone = 'N/A'
        information = {
            'Single header' : single_header,
            'Single Dealer Num' : single_dealer_num,
            'Dealer Name' : name,
            'Phone' : phone,
            'Address' : address_cus,
            'City' : city,
            'State' : state,
            'Dealer Full Address' : full_address,
            'Zip' : zip_code,
            'About Dealer' : review_text,
            'Image' : img_src,
            'Radius' : radius,
            'Rating' : rating,
            'Review Count' : review_count_only,
            'View inventory' : inventory_link_cus,
        }

        single_all_data.append(information)
        
        # Scroll down the page
        scroll_down_slowly(driver)
        print(information)
        print("*"*50)
        
        # time.sleep
        # dealer_id = "D-24770071"
        # Insert into SQLite
        cursor.execute('''
            INSERT INTO dealers (dealer_id,name, phone, address, city, state, dealer_full_address, dealer_iframe_map, zip, about_me, img, radius, rating, review_count_only, inventory_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dealer_id, name, phone, address, city, state, address_cus, dealer_iframe_map, zip_code, review_text, img_src, radius, rating, review_count_only, inventory_link_cus))
        conn.commit()

        # Write to dealers CSV
        dealer_csv_writer[1].writerow([dealer_id, name, phone, full_address, city, state, address_cus, dealer_iframe_map, zip_code, review_text, img_src, radius, rating, review_count_only, inventory_link_cus ])

    return single_all_data
    try:
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="content"]'))
        )
    except AttributeError as e :
        logging.error("Timeout waiting for page to load: %s", e)
        driver.quit()
        sys.exit(1)

    logging.info("Fetching webpage content with requests")

    try:
        inventory_num = data.find_element(By.XPATH,"//h3[contains(text(),'Car Dealerships near')]").text
        dealer_zip = data.find_element(By.XPATH, '//input[@id="select_zip"]')
        dealer_zip_radious = data.find_element(By.XPATH, '//select[@id="select_radius"]')
        # Step 1: Get the current value of the input field
        current_zip_value = dealer_zip.get_attribute('value')
        current_zip_radious_value = dealer_zip_radious.get_attribute('value')

        print("Current inventory number :", inventory_num)
        print("Current value of dealer_zip:", current_zip_value)
        print("Current value of dealer_zip_radious:", current_zip_radious_value)

        print("table data processing...")


        dealer_table_tr = data.find_element(By.XPATH,'//table[@id="dealers_table"]')

        html_content = dealer_table_tr.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        file_path = 'upload/driverbase_dealer_html.txt'

        # Check if the file path exists
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(soup.prettify())
            logging.info(f"HTML content saved to {file_path}")
        else:
            logging.info(f"{file_path} already exists. No file created.")


        dealer_rows = soup.find_all('tr', class_='dealer_row')
        for row in dealer_rows:
            # Extract dealer title
            title = row.find('a').get_text(strip=True)

            # Extract radius (look for the text that contains "miles away")
            radius_element = row.find('span', class_='meta')
            if radius_element:
                radius_text = radius_element.get_text(strip=True)
                radius_parts = radius_text.split()
                # Ensure there's enough text to form the radius output
                if 'miles' in radius_text:
                    radius = radius_text.split("miles")[0].strip() + " miles away"
                else:
                    radius = "N/A"
            else:
                radius = "N/A"

            # Extract phone number
            phone_element = row.find('a', href=lambda href: href and href.startswith('tel:'))
            phone = phone_element.get_text(strip=True) if phone_element else "N/A"

            # Extract address
            address_element = row.find('a', href=lambda href: 'maps' in href)
            address = address_element.get_text(strip=True) if address_element else "N/A"
            
            # Retrieve the text of the second h3 (if needed)
            second_h3 = row.find('h3').find_next('h3')
            listing_info = second_h3.get_text(strip=True)

            # Get the sibling span elements with the class 'meta'
            status_details = [span.get_text(strip=True) for span in second_h3.find_next_siblings('span', class_='meta')]
            status_details_string = ', '.join(status_details)

            # Extract dealer inventory link
            inventory_link_element = row.find('a', href=lambda href: 'inventory' in href)
            inventory_link = inventory_link_element.get('href')
            if inventory_link_element:
                base_url = 'https://driverbase.com'
                custom_url = base_url + inventory_link
            else:
                inventory_link = "N/A"

            all_data = []
            
            dealer_info = extract_vehicle_info(custom_url,driver, conn, cursor, csv_writers, all_data, header_data)
            # print(dealer_info) URL,driver, conn, cursor, csv_writers, all_data, header_data
            # sys.exit()

            # # Extract dealer website link
            all_links = row.find_all('a', href=True)
            # Get the last <a> tag's href
            if all_links:
                website_link = all_links[-1].get('href')  # Get the href of the last link
            else:
                website_link = "N/A"


            # Format and print the result
            print(f"Title: {title}")
            print(f"Radius: {radius}")
            print(f"Phone: {phone}")
            print(f"Address: {address}")
            print(f"Listing number: {listing_info}")
            print(f"Status details: {status_details_string}")
            print(f"Dealer Inventory: {custom_url}")
            print(f"Dealer Website: {website_link}\n")
            


            dealer_id = "D-24770071"
            # Insert into SQLite
            cursor.execute('''
                INSERT INTO dealers (dealer_id,title, radius, phone, address, listing_info, status_details, custom_url, website_link)
                VALUES (?,?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dealer_id, title, radius, phone, address, listing_info, status_details_string, custom_url, website_link))
            conn.commit()

            # dealer_id = cursor.lastrowid 

            # Write to dealers CSV
            csv_writers[0].writerow([dealer_id, title, radius, phone, address, listing_info, status_details_string, custom_url, website_link])

            # Write to CSV
            # csv_writer.writerow([title, radius, phone, address, listing_info, status_details_string, inventory_link, website_link])
        data.quit()
        time.sleep(3)

    except AttributeError:
        inventory_num = ''

    # all_data = []
    ### *** step 0000
    # data = extract_vehicle_info(URL,driver, all_data, HEADER)
    # data = extract_vehicle_info(URL,driver, conn, cursor, csv_writers, all_data, header_data)

    return all_data

def main():
    # Set up logging (optional)
    logging.basicConfig(level=logging.INFO)
    
    conn, cursor, dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer  = setup_db_and_csv()
    # conn, cursor, dealer_csv_file, dealer_csv_writer  = setup_db_and_csv()

    main_driver = initialize_webdriver()
    targated_url = custom_url()

    URL = targated_url
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(URL)
    main_driver.get(URL)

    driver = WebDriverWait(main_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="addressTyped"]')))

    input_element = driver.find_element(By.XPATH, '//input[@id="addressTyped"]')
    input_element.clear()
    # input_element.send_keys("77007") 
    # input_element.send_keys("78205") 
    input_element.send_keys("78702") 

    select_element = driver.find_element(By.XPATH, '//select[@id="refine-search-distance"]')
    select = Select(select_element)
    # select.select_by_value("50")
    select.select_by_value("10")


    logging.info("Filled out the form fields")


    submit_button = WebDriverWait(main_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )
    submit_button.click()

    logging.info("Clicked the submit button")

    # single_driver = WebDriverWait(main_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//section[@class="results"]')))
    # URL, driver, conn, cursor, csv_writers, all_data, header_data
    single_all_data = []
    extract_dealer_info(main_driver, conn, cursor, (dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer), single_all_data, HEADER)

        # Loop through pages
    number_of_pages = 3
    for page in range(1, number_of_pages):
        if not navigate_to_next_page(main_driver, page):
            break
        extract_dealer_info(main_driver, conn, cursor, (dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer), single_all_data, HEADER)

    print(single_all_data)
    print('*'*40)
    time.sleep(10)
    main_driver.quit()

    # dealer_csv_file.close()   blade
    # inventory_csv_file.close()
    # inventory_details_csv_file.close()

    # Clean up: Close the database connection
    # conn.close()

if __name__ == "__main__":
    main()