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
from mysql_connector import get_mysql_connection


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
    file_path = "upload/"
    db_name = "driverbase_data.db"
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
            email TEXT,
            phone TEXT,
            dealer_full_address TEXT,
            city TEXT,
            state TEXT,
            address TEXT,
            dealer_iframe_map TEXT,
            zip TEXT,
            country TEXT,
            about_me TEXT,
            image TEXT,
            radius TEXT,
            listing_info TEXT,
            status_details TEXT,
            custom_url TEXT,
            website_link TEXT
        )
    ''')

    ### *** step 01       FOREIGN KEY(dealer_id) REFERENCES dealers(id),
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_url TEXT,
            base_url TEXT,
            link TEXT,
            cus_link TEXT,
            vehicle_name TEXT,
            status TEXT,
            price TEXT,
            miles TEXT,
            join_details TEXT,
            vin TEXT,
            stock TEXT,
            mpg_city TEXT,
            mpg_highway TEXT,
            engine TEXT,
            transmission TEXT,
            image_src TEXT,
            local_image_path TEXT,
            dealer_href TEXT,
            dealer_text TEXT,
            days_text TEXT,
            views_text TEXT,
            dealer_detail_full_name TEXT,
            dealer_detail_google_map_link TEXT,
            dealer_detail_telephone_no TEXT,
            dealer_detail_listing_no TEXT,
            dealer_detail_listing_status TEXT,
            dealer_detail_link TEXT,
            dealer_detail_website_link TEXT,
            dealer_detail_about_text TEXT,
            dealer_detail_about_details TEXT
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
    dealer_csv_file = open('upload/dealers_info.csv', mode='a', newline='', encoding='utf-8')
    inventory_csv_file = open('upload/inventory_info.csv', mode='a', newline='', encoding='utf-8')

    ### *** step 02
    # inventory_details_csv_file = open('upload/inventory_details.csv', mode='a', newline='', encoding='utf-8')

    dealer_csv_writer = csv.writer(dealer_csv_file)
    inventory_csv_writer = csv.writer(inventory_csv_file)

    ### *** step 03
    # inventory_details_csv_writer = csv.writer(inventory_details_csv_file)

    # Write headers if files are empty
    if os.stat('upload/dealers_info.csv').st_size == 0:
        dealer_csv_writer.writerow(['Dealer ID', 'Name','Email', 'Phone', 'Dealer Full Address', 'City', 'State', 'Address', 'Dealer Iframe Map', 'Zip Code', 'Country', 'About Me', 'Image', 'Radius', 'Listing Info', 'Status Details', 'Custom url', 'Website Link'])

    if os.stat('upload/inventory_info.csv').st_size == 0:
        inventory_csv_writer.writerow(['Main URL', 'Base URL', 'Link', 'Custom Link', 'Vehicle Name', 'Status', 'Price', 'Miles', 'Join Details', 
                                        'VIN', 'Stock', 'MPG CIty', 'MPG Highway', 'Engine', 'Transmission', 'Image src', 'Local Image Path', 'Dealer href',
                                        'Dealer Text', 'Views Text', 'Dealer Detail full Name', 'Dealer Detail google map', 'Dealer Detail Telephone', 
                                        'Dealer Detail Listing No', 'Dealer Detail  Listing Status', 'Dealer Detail Link', 'Dealer Detail Website Link', 
                                        'Dealer Detail About Text', 'Dealer Detail About Details'])
    ### *** step 04
    # if os.stat('upload/inventory_details.csv').st_size == 0:
    #     inventory_details_csv_writer.writerow(['Inventory ID', 'Detail Key', 'Detail Value'])

    return conn, cursor, dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer

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
        return "D-24770071" 

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

def custom_url(zip_code,zip_radius):
    base_url = "https://driverbase.com/"
    addition_url = f"dealers/map?search.Zip={zip_code}&search.DistanceFromZip={zip_radius}"
    targated_url  = base_url+addition_url

    return targated_url


def get_page_content_hash(driver):
    """Generate a hash of the current page's content to detect duplicates."""
    page_content = driver.page_source
    return hashlib.md5(page_content.encode('utf-8')).hexdigest()



def navigate_to_next_page(driver, page_number):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//form[@id="vlp_form"]//div//span[2]//button[2]'))
        )
        next_button.click()

                
        # Wait for the next page to load before continuing
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//table[@id="inventory_vehicles_table"]'))
        )
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
    


def scroll_down_slowly(driver, scroll_pause_time=0.5, step=400):
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



# remote_image_url,local_directory,local_image_path
def download_image(remote_url, directory_location, local_image_path):
    time.sleep(3)
    # Check if the file already exists
    if os.path.exists(local_image_path):
        print(f"Image already exists at {local_image_path}, skipping download.")
        return  # Skip downloading the image if it exists

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





def scrape_detail_page(driver, vehicle_data, single_vehicle_data,link):
    """
    Scrapes detailed page for a single vehicle entry.
    """
        
    main_url = single_vehicle_data['Main Url']
    base_url = single_vehicle_data['Base Url']

     # Click the link to open the details page
    driver.execute_script("window.open(arguments[0], '_blank');", link)
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab


    # return driver,main_url,base_url, replace_title_whitespace, vin_info, stock_info 
    # Wait for the detail page to load and scrape data (add your detailed page scraping logic here)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@id='content']")))
        # Add your scraping logic here for the detailed page

        # Example: Scrape more data from the detailed page
        detail_title = driver.find_element(By.XPATH, "//header//div//div[2]//div[2]//h1").text  
        detail_price = driver.find_element(By.XPATH, "//header//div//div[2]//div[2]//h3").text  
        detail_monthly_pay = driver.find_element(By.XPATH, "//span[@id='pmt']").text  

        detail_status_span = driver.find_elements(By.XPATH, "//span")
        detail_possible_statuses = ["New", "Preowned", "Certified Preowned"]
        detail_status = "Not Found"
        detail_engine = "Not Found"
        for detail_span in detail_status_span:
            detail_span_text = detail_span.text.strip()
            if detail_span_text in detail_possible_statuses:
                detail_status = detail_span_text

                parent_element = detail_span.find_element(By.XPATH, '..')
                parent_text = parent_element.text.strip()
                detail_engine = parent_text.replace(detail_status, '').strip()
                break
            

        detail_dealer_link_tag = driver.find_element(By.XPATH, "//a[contains(@href, '/dealers/id/')]")

        detail_dealer_href =  detail_dealer_link_tag.get_attribute('href') if detail_dealer_link_tag else "Dealer link not found"
        detail_dealer_text = detail_dealer_link_tag.text.strip() if detail_dealer_link_tag else "Dealer text not found"
        detail_dealer_phone = driver.find_element(By.XPATH, "//header//div//div[2]//div[2]//div[3]//div//a[1]//button//span[2]").text  

        # --- Scraping for "Number of days on driverbase" ---
        detail_days_text = driver.find_element(By.XPATH, "//span[starts-with(@id,'dayslisted')]").text

        # --- Scraping for "glyphicon-eye-open" views ---
        detail_views_span = driver.find_element(By.XPATH, "//span[contains(@class, 'glyphicon-eye-open')]")
        detail_views_text = detail_views_span.find_element(By.XPATH, "following-sibling::small").text.strip() if detail_views_span else "Views not found"

        detail_rows = driver.find_elements(By.XPATH,'//table[@id="sort"]//tbody//tr')

        vehicle_details = {}
        for row in detail_rows:
            key_element = row.find_element(By.XPATH, './td[1]')  # First <td> is the key
            value_element = row.find_element(By.XPATH, './td[2]')  # Second <td> is the value
            # Extract the text from the elements
            key = key_element.text.strip().replace(":", "")  # Remove the colon from the key
            value = value_element.text.strip()
            # Add the key-value pair to the dictionary
            vehicle_details[key] = value
        
        
        try:
            detail_dealer_web_link = driver.find_element(By.XPATH, '//span[@class="col-xs-6 meta"]//a').get_attribute('href')
        except Exception as e:
            print(f"Error fetching dealer web link: {e}")
        
        # --- Scraping for "glyphicon-map-marker" (dealer name) ---
        try:
            # Locate the element by class name
            detail_dealer_name = driver.find_element(By.CLASS_NAME, 'glyphicon-map-marker')
            dealer_button = detail_dealer_name.find_element(By.XPATH, 'following-sibling::button')
            detail_dealer_name_text = dealer_button.text.strip()
        except Exception as e:
            detail_dealer_name_text = "Dealer Name not found"
        # --- Scraping for "glyphicon-map-marker" (dealer name) ---

        try:
            # Locate the element by class name
            detail_dealer_comment = driver.find_element(By.XPATH, '//header//div//div[2]/div[5]/span').text.strip()
        except Exception as e:
            detail_dealer_comment = "Dealer Comment not found"
        
        replace_title_whitespace = detail_title.replace(' ', '_').replace('/', '_').replace('-', '_')
        # vin_info = single_vehicle_data['VIN']
        # stock_info = single_vehicle_data['Stock']
        vin_info = vehicle_details['VIN #']
        stock_info = vehicle_details['Stock #']
        print(replace_title_whitespace)
        print(vin_info)
        print(stock_info)
        try:
            replace_title_whitespace = detail_title.replace(' ', '_').replace('/', '_').replace('-', '_')
            # vin_info = single_vehicle_data['VIN']
            # stock_info = single_vehicle_data['Stock']
            vin_info = vehicle_details['VIN #'].replace(' [check for recalls]','')
            stock_info = vehicle_details['Stock #']

            img_stack = driver.find_element(By.XPATH, '//img[@src="/public/img/icn/img-stack.png"]')
            img_stack_src = img_stack.get_attribute('src')
            print(f"Image stack src: {img_stack_src}")
            sibling_images = img_stack.find_elements(By.XPATH, '../../following-sibling::div//img')
            sibling_image_sources = [img.get_attribute('src') for img in sibling_images]
            image_sources_str = ",".join(sibling_image_sources)

            # Print all sibling image sources found
            downloaded_image_paths = []
            for idx, img_src in enumerate(sibling_image_sources[:5], 1):
                print(f"Attempting to download image {idx} from {img_src}") 
                location_url = main_url.split('/')[-1]
                directory_location = 'uploads/'+location_url.replace('/','_').replace('-', '_')+'/'+vin_info
                detail_local_image_path = f"{directory_location}/{replace_title_whitespace + '_' + vin_info + '_' + stock_info}_{idx}.jpg" 
                download_image(img_src, directory_location, detail_local_image_path)
                downloaded_image_paths.append(detail_local_image_path)
                print(f"Sibling image {idx} src: {img_src}")

        except Exception as e:
            print(f"Error fetching images: {e}")

        # Print the extracted details
        for key, value in vehicle_details.items():
            print(f"{key}: {value}")

        detail_vehicle_info = []

        detail_info = {
            'detail_title' : detail_title,
            'detail_price' : detail_price,
            'detail_status' : detail_status,
            'detail_engine' : detail_engine,
            'detail_monthly_pay' : detail_monthly_pay,
            'detail_dealer_href' : detail_dealer_href,
            'detail_dealer_name' : detail_dealer_text,
            'detail_dealer_phone' : detail_dealer_phone,
            'detail_days_text' : detail_days_text,
            'detail_views_text' : detail_views_text,
            'detail_dealer_web_link' : detail_dealer_web_link,
            'detail_dealer_name_text' : detail_dealer_name_text,

            'detail_dealer_comment' : detail_dealer_comment,
            'downloaded_image_paths' : downloaded_image_paths,

        }
        detail_vehicle_info.append(detail_info)
        detail_vehicle_info.append(vehicle_details)
        time.sleep(3)

    except Exception as e:
        print(f"Error fetching details from the page: {e}")
    
    # # Close the detail tab and switch back to the main window
    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])

    window_handles = driver.window_handles

        # Close the last (third) tab
    driver.switch_to.window(window_handles[2])  # Switch to the last tab
    driver.close()  # Close the last tab

    # Switch to the second tab
    driver.switch_to.window(window_handles[1])
    return detail_vehicle_info
        


def extract_vehicle_info(URL, driver, conn, cursor, csv_writers, all_data, header_data):

    inventories_count = 0 
    if URL:
        driver.execute_script("window.open(arguments[0], '_blank');", URL)
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab

    try:
        # while True:  # Loop through pages
            data = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//table[@id="inventory_vehicles_table"]'))
            )
        # # *********************************  Work till *******************************************
        # try:
            logging.info("Fetching webpage content with requests")

            dealer_detail_obj = data.find_element(By.XPATH,'//div[@id="content"]//header')
            dealer_detail_full_name = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[1]//h1').text
            dealer_detail_google_map_link = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[1]//span//a[1]').text
            dealer_detail_telephone_no = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[1]//span//a[2]').text
            dealer_detail_listing_no = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[2]//h3[1]').text
            dealer_detail_listing_status = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[2]//h3[2]').text
            dealer_detail_link = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[2]//div//span[1]//a').get_attribute('href')
            dealer_detail_website_link = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[1]//div[2]//div//span[2]//a').get_attribute('href')
            dealer_detail_about_text = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[5]//h2').text
            dealer_detail_about_details = dealer_detail_obj.find_element(By.XPATH,'//div[2]//div[5]//p').text
            
            # address_obj = data.find_element(By.XPATH,"//form[@id='vlp_form']//div//h1").text
            # custom_address_obj = address_obj.replace('Cars for Sale Near ','')
            # custom_addrtess_split = custom_address_obj.split(',')
            # custom_city = custom_addrtess_split[0]
            # custom_state = custom_addrtess_split[1].replace(' ', '')
            # zip_obj = data.find_element(By.XPATH,"//form[@id='vlp_form']//input[@id='select_zip']").get_attribute('value')
            
            # return URL, data, address_obj, custom_city, custom_state, zip_obj
            # table_obj = data.find_elements(By.XPATH,'//tbody//tr')

            html_content = data.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            file_path = 'upload/driverbase_html.txt'


            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(soup.prettify())

                logging.info(f"HTML content saved to {file_path}")
            else:
                logging.info(f"{file_path} already exists. No file created.")

            rows = soup.find_all('tr', class_='inventory_row')

            single_all_data = []
            for row in rows:
                inventories_count += 1 

                base_url = "https://driverbase.com"
                link = row.find('a', href=True)['href']
                cus_link = base_url + link
                vehicle_name = row.find('h2').text.strip()

                status_span = row.find_all('span')
                possible_statuses = ["New", "Preowned", "Certified Preowned"]
                status = "Not Found"
                for span in status_span:
                    span_text = span.text.strip()
                    if span_text in possible_statuses:
                        status = span_text
                        break

                price = row.find('h4').text.strip()
                details = [detail.text.strip() for detail in row.find_all('small')]

                miles_elements = row.find_all('h4')
                miles = miles_elements[1].text.strip() if len(miles_elements) > 1 else None
                # # Extract the second h4 text
                # if len(miles_elements) > 1:
                #     miles = miles_elements[1].text.strip()
                # else:
                #     miles = None

                details_data = row.find_all('small')
                vin = stock = mpg_city = mpg_highway = engine = transmission = "Not found"
                for detail in details_data:
                    detail_text = detail.text.strip()
                    
                    # VIN
                    if detail_text.startswith("VIN"):
                        vin = detail_text.replace('VIN: ','')
                    
                    # Stock
                    elif detail_text.startswith("Stock"):
                        stock = detail_text.replace('Stock: ','')
                    
                    # MPG City/Highway
                    elif "MPG" in detail_text:
                        mpg_info = detail_text.split(',')
                        if len(mpg_info) == 2:
                            mpg_city = mpg_info[0].replace("MPG: City ", "")
                            mpg_highway = mpg_info[1].replace(" Highway: ", "")

                    # Engine
                    elif "Cylinders" in detail_text:
                        engine = detail_text

                    # Transmission
                    elif "Speed" in detail_text:
                        transmission = detail_text

                # If engine information was not found
                if engine == "Not found":
                    engine = "N/A"

                # If transmission information was not found
                if transmission == "Not found":
                    transmission = "N/A"

                single_title = vehicle_name

                directory_location = 'uploads/single_image'
                vin_info = vin
                stock_info = stock

                replace_title_whitespace = single_title.replace(' ', '_').replace('/', '_').replace('-', '_')
                local_image_path = f"{directory_location}/{replace_title_whitespace + '_'+ vin_info + '_' +stock_info}.jpg"
                # --- Wait for the image to load ---
                try:
                    # Explicitly wait for the image to have a `src` attribute
                    image_tag = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//img[@class='lazy']"))
                    ) 
                    image_src = image_tag.get_attribute('src') if image_tag else "Image not found"

                    download_image(image_src, directory_location, local_image_path)
                except:
                    image_src = "Image not found"

                # Extract dealer link and text dynamically
                dealer_link_tag = row.find('a', href=lambda href: href and "/dealers/id/" in href)  # Find <a> tags with "/dealers/id/" in the href
                
                dealer_href = base_url + dealer_link_tag['href'] if dealer_link_tag else "Dealer link not found"
                dealer_text = dealer_link_tag.text.strip() if dealer_link_tag else "Dealer text not found"

                # --- Scraping for "Number of days on driverbase" ---
                days_on_driverbase = row.find('img', alt="Number of days on driverbase")
                days_text = days_on_driverbase.find_next('span').text.strip() if days_on_driverbase else "Days on driverbase not found"

                # --- Scraping for "glyphicon-eye-open" views ---
                views_span = row.find('span', class_="glyphicon glyphicon-eye-open")
                views_text = views_span.find_next('small').text.strip() if views_span else "Views not found"

                join_details = ', '.join(details)

                single_vehicle_data = {
                    'Main Url': URL,
                    'Base Url': base_url,
                    'link': link,
                    'cus_link': cus_link,
                    'single_title': vehicle_name,
                    'Status': status,
                    'Price': price,
                    'Miles': miles,
                    'single_details': join_details,
                    'VIN': vin,
                    'Stock': stock,


                    'MPG City': mpg_city,
                    'MPG Highway': mpg_highway,
                    'Engine': engine,
                    'Transmission': transmission,
                    'Image Path': image_src,


                    'local Image Path': local_image_path,
                    'Dealer Link': dealer_href,
                    'Dealer Name': dealer_text,
                    'Days on Driverbase': days_text,
                    'Views': views_text,
                    'dealer_detail_full_name': dealer_detail_full_name,
                    'dealer_detail_google_map_link': dealer_detail_google_map_link,
                    'dealer_detail_telephone_no': dealer_detail_telephone_no,
                    'dealer_detail_listing_no': dealer_detail_listing_no,
                    'dealer_detail_listing_status': dealer_detail_listing_status,
                    'dealer_detail_link': dealer_detail_link,
                    'dealer_detail_website_link': dealer_detail_website_link,
                    'dealer_detail_about_text': dealer_detail_about_text,
                    'dealer_detail_about_details': dealer_detail_about_details,

                    # 'address_obj': address_obj,
                    # 'zip_obj': zip_obj,
                    # 'custom_address_obj': custom_address_obj,
                    # 'custom_city': custom_city,
                    # 'custom_state': custom_state,
                }

                scroll_down_slowly(driver)

                
                # Append the single vehicle's data to all_data
                # csv_writers.writerow(single_vehicle_data.values())
                single_all_data.append(single_vehicle_data)

                detail_vehicle_data =[]
                infor = scrape_detail_page(driver, detail_vehicle_data, single_vehicle_data, link)
                
                # print(infor)
                print('*'*40)


                # Insert into SQLite
                cursor.execute('''
                    INSERT INTO vehicles (main_url, base_url, link, cus_link, vehicle_name, status, price, miles, join_details, 
                                            vin, stock, mpg_city, mpg_highway, engine, transmission, image_src, local_image_path, dealer_href ,
                                            dealer_text, days_text, views_text, dealer_detail_full_name, dealer_detail_google_map_link, 
                                            dealer_detail_telephone_no, dealer_detail_listing_no, dealer_detail_listing_status, dealer_detail_link, 
                                            dealer_detail_website_link, dealer_detail_about_text, dealer_detail_about_details
                                        )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?)
                ''', (URL, base_url, link, cus_link, vehicle_name, status, price, miles, join_details, 
                        vin, stock, mpg_city, mpg_highway, engine, transmission, image_src, local_image_path, dealer_href, 
                        dealer_text, days_text, views_text, dealer_detail_full_name, dealer_detail_google_map_link, 
                        dealer_detail_telephone_no, dealer_detail_listing_no, dealer_detail_listing_status, dealer_detail_link, 
                        dealer_detail_website_link, dealer_detail_about_text, dealer_detail_about_details
                    ))
                conn.commit()

                # dealer_id = cursor.lastrowid 

                # Write to dealers CSV
                csv_writers[1].writerow([URL, base_url, link, 
                                        cus_link, vehicle_name, status,
                                        price, miles, join_details, 
                                        vin, stock, mpg_city, 
                                        mpg_highway, engine, transmission, 
                                        image_src, local_image_path, dealer_href, 
                                        dealer_text, days_text, views_text, 
                                        dealer_detail_full_name, dealer_detail_google_map_link, dealer_detail_telephone_no, 
                                        dealer_detail_listing_no, dealer_detail_listing_status, dealer_detail_link, 
                                        dealer_detail_website_link, dealer_detail_about_text, dealer_detail_about_details])

            # # # vehicle_data = (
            # # #     'vehicle_name', 'status', 'price', 'vin', 'stock', 'mpg_city', 'mpg_highway', 'engine', 
            # # #     'transmission', None, 'days_on_driverbase', 'views', 'image_url', 'custom_link', 
            # # #     'detail_price', 'detail_status', 'detail_engine', 'local_image_path', 'downloaded_image_paths'
            # # # )
            # # # dealer_data = (
            # # #     'dealer_href', 'dealer_text', 'detail_dealer_phone'
            # # # )
            # # # return vehicle_data, dealer_data



            number_of_pages = 2  # Set the number of pages you want to scrape
            for page in range(number_of_pages):
                logging.info(f"Scraping page {page + 1}")
                # Scrape the current page
                extract_vehicle_info(None, data, conn, cursor, csv_writers, all_data, header_data)
                # (Add your scraping logic here for the current page)

                # Navigate to the next page
                if not navigate_to_next_page(driver, page):
                    logging.info("No more pages to navigate.")
                    break

    except Exception as e:
        logging.error(f"Error occurred while extracting vehicle information: {e}")

    finally:
         # Close the tab and switch back to the original tab
        if len(driver.window_handles) > 1:
            driver.close()  # Close the current tab
            driver.switch_to.window(driver.window_handles[0])  # Switch back to the main window
        else:
            logging.info("No new tabs to close.")

def extract_dealer_info(URL, driver, conn, cursor, csv_writers, all_data, header_data):
    
    inventories_count = 0 
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
            dealer_name = row.find('a').get_text(strip=True)

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
            full_address = address_element.get_text(strip=True) if address_element else "N/A"
    
             # Split the address into parts based on newline and commas
            # Get the full address without the radius part
            address_details = full_address.split(',')             # Split the actual address by commas
            country = address_details[-1].strip()                  # Extract the city, state, and zip from the last two parts # Always the second to last part
            city = address_details[-3].strip()                  # Extract the city, state, and zip from the last two parts # Always the second to last part
            state_zip = address_details[-2].strip().split()  # The last part contains state and zip
            state = state_zip[0]  # State (e.g., 'TX')
            zip_code = state_zip[1]  # Zip code (e.g., '78237')
            cus_address = ', '.join(address_details[:-3]).strip()  # The address before city


            # Check if dealer already exists
            existing_dealer_id = get_existing_dealer_id(cursor, dealer_name, full_address, zip_code)
            if existing_dealer_id:
                dealer_id = existing_dealer_id  # Use existing dealer ID
            else:
                dealer_id = get_new_dealer_id(cursor)  # Generate a new unique dealer ID

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
            print(f"Title: {dealer_name}")
            print(f"Radius: {radius}")
            print(f"Phone: {phone}")
            print(f"Address: {full_address}")
            print(f"Listing number: {listing_info}")
            print(f"Status details: {status_details_string}")
            print(f"Dealer Inventory: {custom_url}")
            print(f"Dealer Website: {website_link}\n")
            

            scroll_down_slowly(driver)
            # dealer_id = "D-24770071"
            dealer_iframe_map = "N/A"
            about_me = "N/A"
            image = "N/A"
            email = "N/A"
            # Insert into SQLite
            cursor.execute('''
                INSERT INTO dealers (dealer_id,  name, email, phone, address, city, state, dealer_full_address, dealer_iframe_map, zip, country, about_me, image, radius, listing_info, status_details, custom_url, website_link)
                VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dealer_id, dealer_name, email, phone, full_address, city, state, cus_address, dealer_iframe_map, zip_code, country, about_me, image, radius, listing_info, status_details_string, custom_url, website_link))
            conn.commit()

        #  cursor.execute('''
        #     INSERT INTO dealers (dealer_id,name, phone, address, city, state, dealer_full_address, dealer_iframe_map, zip, about_me, img, radius, rating, review_count_only, inventory_link)
        #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        # ''', (dealer_id, name, phone, address, city, state, address_cus, dealer_iframe_map, zip_code, review_text, img_src, radius, rating, review_count_only, inventory_link_cus))
        # conn.commit()

            # dealer_id = cursor.lastrowid 

            # Write to dealers CSV
            csv_writers[0].writerow([dealer_id, dealer_name, email, phone, full_address, city, state, cus_address, dealer_iframe_map, zip_code, country, about_me, image, radius, listing_info, status_details_string, custom_url, website_link])

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
    

    # Setup SQLite and CSV writers
     ### *** step 00
    # conn, cursor, dealer_csv_file, inventory_csv_file, inventory_details_csv_file, dealer_csv_writer, inventory_csv_writer, inventory_details_csv_writer = setup_db_and_csv()
    conn, cursor, dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer  = setup_db_and_csv()

    # conn, cursor, dealer_csv_file, csv_writer = setup_db_and_csv()
    # conn, cursor, vehicle_csv_file, dealer_csv_file = setup_db_and_csv()
    
    # url_input = input('Write or Paste your URL : ')
    driver = initialize_webdriver()
    targated_url = custom_url(zip_code = 77007,zip_radius = 50)

    URL = targated_url
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(URL)
    driver.get(URL)
    logging.info("Waiting for the page to load")

    dealer_data = []

    # extract_dealer_info(URL, driver, conn, cursor, (dealer_csv_writer, inventory_csv_writer, inventory_details_csv_writer), dealer_data, HEADER)
    extract_dealer_info(URL, driver, conn, cursor, (dealer_csv_writer, inventory_csv_writer,), dealer_data, HEADER)

    # Close all files and connections
    driver.quit()
    dealer_csv_file.close()
    inventory_csv_file.close()
    # inventory_details_csv_file.close()
    # Clean up: Close the database connection
    conn.close()

if __name__ == "__main__":
    main()