from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, InvalidSessionIdException, WebDriverException
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

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


log_file_path = 'error_log.log'
logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def setup_db_and_csv(zip_code_input):
    # Connect to SQLite database (creates a new database if it doesn't exist)
    file_path = f"public/db/{zip_code_input}/"
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
            dealer_id TEXT, name TEXT, phone TEXT, address TEXT, city TEXT, 
            state TEXT, dealer_full_address TEXT, dealer_iframe_map TEXT, zip TEXT, about_me TEXT,
            img TEXT, local_img TEXT, radius TEXT, rating TEXT, review_count_only TEXT, inventory_link TEXT, batch INTEGER, status INTEGER
        )
    ''')
    # ### *** step 01             FOREIGN KEY(dealer_id) REFERENCES dealers(id),  inventory_link, single_img,  batch, status
    # this make as like our old csv 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, dealer_id INTEGER NULL, dealer_name VARCHAR(255) NULL, phone VARCHAR(255) NULL,description TEXT, 
            dealer_address TEXT, city TEXT, state TEXT, dealer_iframe_map TEXT, zip_code INTEGER NULL,
            a_href TEXT, single_img_src TEXT, local_image_path TEXT, title TEXT, year VARCHAR(255) NULL, 
            make VARCHAR(255) NULL, model VARCHAR(255) NULL, vin VARCHAR(255) NULL, price VARCHAR(255) NULL, mileage VARCHAR(255) NULL,
            vehicle_type VARCHAR(255) NULL, model_no VARCHAR(255) NULL, trim TEXT, stock_number TEXT, engine VARCHAR(255) NULL,
            transmission VARCHAR(255) NULL, body_type VARCHAR(255) NULL, fuel_type VARCHAR(255) NULL, driveInfo VARCHAR(255) NULL, mpg_city VARCHAR(255) NULL,
            mpg_highway VARCHAR(255) NULL, exterior_color VARCHAR(255) NULL, star VARCHAR(255) NULL, created_date TEXT, batch_no TEXT,
            cus_inventory_link VARCHAR(255) NULL, payment VARCHAR(255) NULL, in_market VARCHAR(255) NULL, mpg VARCHAR(255) NULL, interior_color VARCHAR(255) NULL,
            drivetrain VARCHAR(255) NULL, status_text VARCHAR(255) NULL, dealer_inventory_count VARCHAR(255) NULL, vehicle_type_info TEXT 
        )
    ''')
    # this make as like our old db 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dealer_id INTEGER NULL, deal_id INTEGER NULL, dealer_name VARCHAR(255) NULL, dealer_number VARCHAR(255) NULL, dealer_comment TEXT,
            dealer_additional_description TEXT, dealer_img_link TEXT, dealer_local_img_link TEXT, dealer_address TEXT, dealer_website_link TEXT,
            dealer_inventory_link TEXT, fb_link TEXT, insta_link TEXT, dealer_city VARCHAR(255) NULL, dealer_state VARCHAR(255) NULL,
            dealer_iframe_map TEXT, zip_code VARCHAR(255) NULL, latitude VARCHAR(255) NULL, longitude VARCHAR(255) NULL, full_address VARCHAR(255) NULL,
            detail_url VARCHAR(255) NULL, img_from_url TEXT, local_img_url TEXT, vehicle_make_id INTEGER NULL, title VARCHAR(255),
            year VARCHAR(255), make VARCHAR(255), model VARCHAR(255), vin VARCHAR(255), price INTEGER,
            miles VARCHAR(255) NULL, type VARCHAR(255) NULL, modelNo VARCHAR(255) NULL, trim VARCHAR(255) NULL, stock VARCHAR(255) NULL,
            engine_details TEXT NULL, transmission VARCHAR(255) NULL, body_description TEXT NULL, fuel VARCHAR(255) NULL, drive_info TEXT NULL,
            mpg_city VARCHAR(255) NULL, mpg_highway VARCHAR(255) NULL, exterior_color VARCHAR(255) NULL, interior_color VARCHAR(255) NULL, star VARCHAR(255) NULL,
            created_date VARCHAR(255) NULL, deal_review_number VARCHAR(255) NULL,
            FOREIGN KEY (deal_id) REFERENCES users(id)
        )
    ''')

    conn.commit()

    # Create CSV files and writers for dealers, inventories, and inventory details
    dealer_csv_file = open(f'public/db/{zip_code_input}/dealers_info.csv', mode='a', newline='', encoding='utf-8')
    inventory_csv_file = open(f'public/db/{zip_code_input}/inventory_info.csv', mode='a', newline='', encoding='utf-8')
    inventory_details_csv_file = open(f'public/db/{zip_code_input}/inventory_details.csv', mode='a', newline='', encoding='utf-8')

    dealer_csv_writer = csv.writer(dealer_csv_file)
    inventory_csv_writer = csv.writer(inventory_csv_file)
    inventory_details_csv_writer = csv.writer(inventory_details_csv_file)

    # Write headers if files are empty
    if os.stat(f'public/db/{zip_code_input}/dealers_info.csv').st_size == 0:
        dealer_csv_writer.writerow(['Dealer ID', 'Dealer Name', 'Phone', 'Address', 'City', 'State', 'Custom Address' , 
                                    'Dealer Iframe Map', 'Zip Code','About Dealer', 'Dealer Image', 'Lical Image','Radius', 'Rating','Review Count', 'Invnetory Link'])

    # this make as like our old csv 
    if os.stat(f'public/db/{zip_code_input}/inventory_info.csv').st_size == 0:
        inventory_csv_writer.writerow(['Dealer ID', 'Dealer Name', 'Dealer Number', 'Dealer Comment', 'Dealer Address', 'Dealer City', 'Dealer State', 'dealer Iframe Map', 'Zip Code', 'Detail URL', 
                                        'Image From URL','Local Image URL', 'Title', 'Year', 'Make', 'Model', 'Vin', 'Price', 'Miles', 'Type', 
                                        'Model No', 'Trim', 'Stock', 'Engine Details', 'Transmission', 'Body Description', 'Fuel', 'Drive Info', 'MPG City', 'MPG Highway', 
                                        'Exterior Color', 'Star', 'Created Date', 'Batch No', 'Dealer Link', 'Monthly Pay', 'In Market', 'MPG', 'Interior Color', 'Drivetrain', 
                                        'Status','Dealer Inventory Count'])

    # this make as like our old db 
    if os.stat(f'public/db/{zip_code_input}/inventory_details.csv').st_size == 0:
        inventory_details_csv_writer.writerow(['Dealer ID', 'Deal ID', 'Dealer Name', 'Dealer Phone', "Dealer Description", ' Dealer Additional Description', 'Dealer Image Link', 'Dealer Local Image Link', 'Detail Dealer Address', 
        'Dealer Website Link', 'Dealer Inventory Link', 'FB Link', 'Insta Link', 'City' , 'State', 'Dealer Iframe Map', 'Zip Code', 'Latitude', 'Longitude', 'Full Address', 'Main Link', 'Detail dealer Image', 'Local Image Link', 
        'Vehicle Make Id', 'Title', 'Year', 'Make', 'Model', 'Vin', 'Price', 'Mileage', 'Condition', 'ModelNo', 'Trim', 'Stock', 'Engine', 'Transmission', 'Body', 'fuel', 'Drivetrain', 'MPG City', 'MPG Highway', 'Exterior Color', 
        'Interior Color', 'Review Rate', 'Create Date', 'Review Number'])

    return conn, cursor, dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer, inventory_details_csv_file, inventory_details_csv_writer



def is_session_valid(driver):
    try:
        driver.current_url  # Attempt to access the current URL
        return True
    except (InvalidSessionIdException, WebDriverException):
        return False
    


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
        return "D-24787021"  # Start from this ID if no dealers exist

# 

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

def initial_zip_code_seter():
        # Display the ZIP code options
    print("[1] 78702 - Austin")
    print("[2] 75241 - Dallas")
    print("[3] 77007 - Houston")
    print("[4] 78205 - San Antonio")

    # Loop until a valid input is received
    while True:
        try:
            zip_code_input = int(input('Choose Your Number (1-4): '))
            
            if zip_code_input == 1:
                zip_code_input_data = 78702
                break
            elif zip_code_input == 2:
                zip_code_input_data = 75241
                break
            elif zip_code_input == 3:
                zip_code_input_data = 77007
                break
            elif zip_code_input == 4:
                zip_code_input_data = 78205
                break
            else:
                print("Invalid input. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Print the selected ZIP code
    print(f"Selected ZIP code: {zip_code_input_data}")
    return zip_code_input_data
            # if not navigate_to_next_page(driver, page, conn, cursor, csv_writers, all_data, header_data):
            

def navigate_to_next_page(driver, page_number, conn, cursor, csv_writers, all_data, header_data):
    time.sleep(5)
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="srp-desktop-page-navigation-next-page"]'))
        )
        next_button.click()
        logging.info(f"Navigating to page {page_number + 2}")
        
        # Wait for the new page to load
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//main[@id="main"]'))
        )
        base_url =  'https://www.cargurus.com'
        current_url = driver.current_url
        fragment = driver.execute_script("return window.location.hash")
        custom_url = current_url.replace(base_url, '') + fragment

        status = 'next'
        extract_vehicle_info(custom_url, driver, conn, cursor, csv_writers, all_data, header_data,status)

        print(f"fragment:{fragment}")
        print(f"current_url:{current_url}")
        print(f"custom_url:{custom_url}")

        time.sleep(5)  # Additional sleep to ensure the new content is fully loaded
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False
    return True


# def navigate_to_next_dealer_page(driver, page_number):
#     try:
#         next_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, '//div[@class="next"]'))
#         )
#         next_button.click()
#         logging.info(f"Navigating to page {page_number + 2}")
        
#         # Wait for the new page to load
#         WebDriverWait(driver, 10).until(
#             EC.staleness_of(next_button)
#         )


#         time.sleep(5)  # Additional sleep to ensure the new content is fully loaded
#     except Exception as e:
#         logging.error(f"Error navigating to the next page: {e}")
#         return False
#     return True

def navigate_to_next_dealer_page(driver, page_number):
    try:
        # Wait for the next button to be clickable (increased timeout to ensure page load)
        next_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="next"]'))
        )
        
        # Check if the next button is displayed and enabled
        if next_button.is_displayed() and next_button.is_enabled():
            next_button.click()
            logging.info(f"Navigating to page {page_number + 2}")
            
            # Wait for the new page to load completely
            WebDriverWait(driver, 15).until(
                EC.staleness_of(next_button)
            )
            
            # Adding extra time to ensure the new content is fully loaded
            time.sleep(5)
        else:
            logging.info("Next button is not enabled or visible. Possibly the last page.")
            return False  # Stop the loop if the next button is not clickable

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



# def count_svg_stars(item):
#     svgs = item.find_all('svg', {'data-testid': 'star-full'})
#     return len(svgs)



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


# scrape_detail_page(driver, conn, cursor, csv_writers, detail_vehicle_data, result,cus_inventory_link)
def scrape_detail_page(driver, conn, cursor, csv_writers, vehicle_data, single_vehicle_data, link):
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

            detail_city, detail_state, detail_dealer_address = 'N/A', 'N/A' , 'N/A' 
            if detail_address_city_state != 'No address' and ',' in detail_address_city_state:
                detail_city, detail_state = map(str.strip, detail_address_city_state.split(','))
                detail_dealer_address = f"{detail_city}, {detail_state}"


            # deal_review = driver.find_element(By.XPATH, "//button[@class='JRPjD _8KIJA QXloi LCpwg7']").text if driver.find_elements(By.XPATH, "//button[@class='JRPjD _8KIJA QXloi LCpwg7']") else 'No review'
            detail_dealer_telephone = driver.find_element(By.XPATH, "//span[@class='RTKKej']").text if driver.find_elements(By.XPATH, "//span[@class='RTKKej']") else 'No telephone'

            # Scrape all images
            detail_dealer_images_elements = driver.find_elements(By.XPATH, "//div[@class='RENFam']//button//img")
            detail_dealer_images = [img.get_attribute('src') for img in detail_dealer_images_elements] if detail_dealer_images_elements else ['No Images']


            # directory_location = "path/to/your/directory"
            # section_vin = 'section_vin_AzBy05698'
            # section_vin = 'section_stock_AzBy05698'
            # location_url = f"{detail_city} _ {detail_state}" if detail_city else 'default_location'
            # directory_location = f'uploads/{location_url}/{section_vin}'
            # detail_local_image_path = f"{directory_location}/{detail_title}_{section_vin}_{section_stock}_{idx}.jpg"

            # # Iterate over each image URL and download it
            # for idx, remote_url in enumerate(detail_dealer_images):
            #     if remote_url == "No Images":
            #         print("No images available.")
            #         continue
            #     detail_local_image_path = os.path.join(directory_location, f"image_{idx}.jpg")

            #     download_image(remote_url, directory_location, detail_local_image_path)


            detail_section_element = driver.find_element(By.XPATH, "//div[@class='Cois5O']")
            detail_section_main_element = detail_section_element.find_element(By.XPATH, "//section[@data-cg-ft='vdp-stats']")

            main_mileage = None
            main_drivetrain = None
            main_exterior_color = None
            main_mpg = None
            main_engine = None
            main_fuel_type = None
            main_transmission = None

            main_data_key_element = detail_section_main_element.find_element(By.XPATH, './div/h5[@class="us1dS _1tWpD"]')
            main_data_key = main_data_key_element.text if main_data_key_element else "No  MAin Key"
            main_data_value_element = detail_section_main_element.find_element(By.XPATH, './div/p[@class="us1dS"]')
            main_data_value = main_data_value_element.text if main_data_value_element else "No  MAin Value"

            if main_data_key == "Mileage":
                main_mileage = main_data_value
            elif main_data_key == "Drivetrain":
                main_drivetrain = main_data_value
            elif main_data_key == "Exterior color":
                main_exterior_color = main_data_value
            elif main_data_key == "MPG":
                main_mpg = main_data_value
            elif main_data_key == "Engine":
                main_engine = main_data_value
            elif main_data_key == "Fuel type":
                main_fuel_type = main_data_value
            elif main_data_key == "Transmission":
                main_transmission = main_data_value

            detail_section_additional_element = detail_section_element.find_elements(By.XPATH, "//section[@data-cg-ft='vdpExtendedStats']")


            print(detail_title, detail_price, detail_city, detail_state, detail_dealer_address, detail_dealer_telephone)
            print(detail_dealer_images)
            print(detail_section_element)
            print(detail_section_main_element)
            print(main_mileage,main_drivetrain,main_exterior_color,main_mpg,main_engine,main_data_key,main_fuel_type,main_transmission)
            print(detail_section_additional_element)
            print('main data scraped '*30)
            sys.exit()

            key_value_list = []
            # Loop through each element in detail_section_additional_element
            for addition_data in detail_section_additional_element:
                try:
                    # Try to find the key (first span element)
                    addition_data_key_element = addition_data.find_element(By.XPATH, './div/ul/li/div/div/span[1]')
                    addition_data_key = addition_data_key_element.text if addition_data_key_element else "No addition Key"

                    # Try to find the value (second span element)
                    addition_data_value_element = addition_data.find_element(By.XPATH, './div/ul/li/div/div/span[1]')
                    addition_data_value = addition_data_value_element.text if addition_data_value_element else "No addition Value"
                
                except Exception as e:
                    # Handle any exception (e.g., element not found)
                    print(f"Error finding key or value: {e}")
                    addition_data_key = "No addition Key"
                    addition_data_value = "No addition Value"

                # Append the key-value pair to the list even if there's an error
                key_value_list.append({"key": addition_data_key, "value": addition_data_value})

            # Print the collected key-value pairs
            print("Collected key-value pairs:")
            for kv_pair in key_value_list:
                print(f"Key: {kv_pair['key']}, Value: {kv_pair['value']}")


            main_result = {
                'main_mileage' : main_mileage,
                'main_drivetrain' : main_drivetrain,
                'main_exterior_color' : main_exterior_color,
                'main_mpg' : main_mpg,
                'main_engine' : main_engine,
                'main_fuel_type' : main_fuel_type,
                'main_transmission' : main_transmission,
                }
            

            print(main_result)
            print('Succcess '*30)
            html_content = detail_section_element.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            file_path = 'public/cargurus_vehicle_detail_html.txt'
            
            print(detail_title,detail_price,detail_city,detail_state,detail_dealer_address, detail_dealer_telephone)
            print(detail_dealer_images)
            print(detail_section_element)
            print("kalu oja "*40)
            sys.exit()

            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(soup.prettify())
                logging.info(f"HTML content saved to {file_path}")
            else:
                logging.info(f"{file_path} already exists. No file created.")

            sys.exit()
                # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all sections and h2 headings
            sections = soup.find_all('section')
            print('Section data submitted')
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


                # detail_dealer_images_elements = driver.find_element(By.XPATH, "//div[@class='OX5fCO']")

                detail_dealer_additional_infos = driver.find_element(By.XPATH, "//section[@class='sWgu3_']")
                if detail_dealer_additional_infos:
                    dealer_html_content = detail_dealer_additional_infos.get_attribute('innerHTML')
                    dealer_soup = BeautifulSoup(dealer_html_content, 'html.parser')

                    # Save the HTML to a file
                    dealer_file_path = 'public/cargurus_vehicle_detail_dealer_html.txt'
                    if not os.path.exists(dealer_file_path):
                        os.makedirs(os.path.dirname(dealer_file_path), exist_ok=True)
                        with open(dealer_file_path, 'w', encoding='utf-8') as file:
                            file.write(dealer_soup.prettify())
                        logging.info(f"HTML content saved to {dealer_file_path}")
                    else:
                        logging.info(f"{dealer_file_path} already exists. No file created.")
                    
                    # Extract the data
                    dealer_img_link = dealer_soup.find("img", {"class": "QrJyuT"})['src'] if dealer_soup.find("img", {"class": "QrJyuT"}) else None
                    dealer_name = dealer_soup.find("a", {"class": "us1dS i5dPf"}).text.strip() if dealer_soup.find("a", {"class": "us1dS i5dPf"}) else None
                    dealer_phone = dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-phone-link"}).text.strip() if dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-phone-link"}) else None
                    dealer_address = dealer_soup.find("span", {"data-track-ui": "dealer-address"}).text.strip() if dealer_soup.find("span", {"data-track-ui": "dealer-address"}) else None
                    address_parts = dealer_address.split(',')

                print(detail_title, detail_price, detail_city, detail_state, detail_dealer_address, detail_dealer_telephone)
                # print(detail_title, detail_price, detail_city, detail_state, detail_dealer_address, deal_review, detail_dealer_telephone)
                print(detail_dealer_images)
                print(detail_section_element)
                print(extracted_data)
                print('extracted_data '*30)


                if len(address_parts) >= 3:
                    zip_code = address_parts[-1].strip()
                    state = address_parts[-2].strip().split(' ')[0]
                    city = address_parts[-3].strip()
                    full_address = ', '.join(part.strip() for part in address_parts[:-3])  # Join remaining parts as the full address
                else:
                    # Handle case where address doesn't have expected format
                    full_address = None
                    city = None
                    state = None
                    zip_code = 78702
                
                if zip_code:
                    country_code = 'us'
                    api_key = '4b84ff4ad9a74c79ad4a1a945a4e5be1'
                    url = f"https://api.opencagedata.com/geocode/v1/json?q={zip_code},{country_code}&key={api_key}"

                    response = requests.get(url)
                    zip_location_data = response.json()

                    # Check if the geometry data exists
                    if 'results' in zip_location_data and len(zip_location_data['results']) > 0 and 'geometry' in zip_location_data['results'][0]:
                        latitude = zip_location_data['results'][0]['geometry']['lat']
                        longitude = zip_location_data['results'][0]['geometry']['lng']
                        city_name = zip_location_data['results'][0]['components'].get('city', '')
                    else:
                        latitude = None
                        longitude = None
                        api_city_name = None
                else:
                    print("No zip code provided.")

                dealer_inventory_link = dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-inventory-link"})['href'] if dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-inventory-link"}) else None
                dealer_website_link = dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-website-link"})['href'] if dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-website-link"}) else None
                fb_link = dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-facebook-link"})['href'] if dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-facebook-link"}) else None
                insta_link = dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-instagram-link"})['href'] if dealer_soup.find("a", {"data-cg-ft": "vdp-dealer-instagram-link"}) else None
                
                # Extract reviews
                review_rate = dealer_soup.find("span", {"class": "us1dS CrxtQ"}).text.strip() if dealer_soup.find("span", {"class": "us1dS CrxtQ"}) else None
                review_number = dealer_soup.find("span", {"class": "us1dS iK3Zj"}).text.strip() if dealer_soup.find("span", {"class": "us1dS iK3Zj"}) else None

                # Extract dealer description and additional information
                dealer_description = dealer_soup.find("p", {"class": "us1dS iK3Zj"}).text.strip() if dealer_soup.find("p", {"class": "us1dS iK3Zj"}) else None
                dealer_additional_description = dealer_soup.find_all("p", {"class": "us1dS iK3Zj"})[1].text.strip() if len(dealer_soup.find_all("p", {"class": "us1dS iK3Zj"})) > 1 else None

                # Create output in JSON format
                dealer_data = {
                    "dealer_img_link": dealer_img_link,
                    "dealer_name": dealer_name,
                    "dealer_phone": dealer_phone,
                    "dealer_address": dealer_address,
                    "dealer_inventory_link": dealer_inventory_link,
                    "dealer_website_link": dealer_website_link,
                    "fb_link": fb_link,
                    "insta_link": insta_link,
                    "review_rate": review_rate,
                    "review_number": review_number,
                    "dealer_description": dealer_description,
                    "dealer_additional_information": dealer_additional_description
                }

                # Output the data
                print(dealer_data)

            # section_mileage = None
            # section_drivetrain = None
            # section_exterior_color = None
            section_interiror_color = None
            section_mpg = None
            section_engine = None
            section_fuel = None
            section_transmission = None
            section_make = None
            section_model = None
            section_year = None
            section_trim = None
            section_body_type = None
            section_condition = None
            section_vin = None
            section_stock = None
            section_fuel_tank_size = None
            section_combined_gas_mileage = None
            section_city_gas_mileage = None
            section_highway_gas_mileage = None
            section_fuel_type = None
            section_fuel_horsepower = None
            section_safety_rating = None
            section_safety_crash_rating = None
            section_safety_side_crash_rating = None
            section_safety_rollover_rating = None
            section_doors = None
            section_front_leg_room = None
            section_back_legroom = None
            section_cargo_volume = None
            section_options = []
            section_history = []
            section_pricing = []

            # Display the extracted data
            for data in extracted_data:
                if data['heading'] == 'Mileage':
                    section_mileage  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Drivetrain':
                    section_drivetrain  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Exterior color':
                    section_exterior_color = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Interior color':
                    section_interiror_color  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'MPG':
                    section_mpg  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Engine':
                    section_engine  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Fuel type':
                    section_fuel = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Transmission':
                    section_transmission   = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Make':
                    section_make  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Model':
                    section_model = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Year':
                    section_year  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Trim':
                    section_trim = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Body type':
                    section_body_type = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Condition':
                    section_condition = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'VIN':
                    section_vin   = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Stock number':
                    section_stock = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Fuel tank size':
                    section_fuel_tank_size = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Combined gas mileage':
                    section_combined_gas_mileage = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'City gas mileage':
                    section_city_gas_mileage  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Highway gas mileage':
                    section_highway_gas_mileage = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Fuel type':
                    section_fuel_type = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Horsepower':
                    section_fuel_horsepower = data['items'][0] if isinstance(data['items'], list) and data['items'] else None


                elif data['heading'] == 'NHTSA overall safety rating':
                    section_safety_rating  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'NHTSA frontal crash rating':
                    section_safety_crash_rating = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'NHTSA side crash rating':
                    section_safety_side_crash_rating = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'NHTSA rollover rating':
                    section_safety_rollover_rating = data['items'][0] if isinstance(data['items'], list) and data['items'] else None


                elif data['heading'] == 'Doors':
                    section_doors  = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Front legroom':
                    section_front_leg_room = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Back legroom':
                    section_back_legroom = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'] == 'Cargo volume':
                    section_cargo_volume = data['items'][0] if isinstance(data['items'], list) and data['items'] else None
                elif data['heading'].lower() == 'options':
                    section_options = data['items']  # Assign the options
                elif data['heading'].lower().startswith('history'):
                    section_history.extend(data['items'])  # Add to history list
                elif data['heading'].lower() == 'pricing':
                    section_pricing = data['items']  # Assign the pricing

                print(f"Section: {data['heading']}")
                if 'items' in data:
                    if isinstance(data['items'], list):
                        for item in data['items']:
                            print(f" - {item}")
                    else:
                        # For sections like Options, History, Pricing, display in one line
                        print(f" - {data['items']}")
                print()

                local_image_path = []
                for idx, single_images_link in enumerate(detail_dealer_images):
                    location_url = f"{detail_city} _ {detail_state}" if detail_city else 'default_location'
                    directory_location = f'uploads/{location_url}/{section_vin}'
                    detail_local_image_path = f"{directory_location}/{detail_title}_{section_vin}_{section_stock}_{idx}.jpg"
                    local_image_path.append(detail_local_image_path)
                    download_image(single_images_link, directory_location, local_image_path)


            # (deal_id) REFERENCES users(id)
                dealer_id = 'DRI241000'
                deal_id = 'DEAL241000'
                modelNo = '#0000'
                dealer_local_img_link = 'dealer_local_img_link'
                dealer_iframe_map = None
                vehicle_make_id = None

                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                # # Insert into SQLitedealer_inventory_link

                cursor.execute('''
                    INSERT INTO vehicles (dealer_id, deal_id, dealer_name, dealer_number, dealer_comment, dealer_additional_description, dealer_img_link, dealer_local_img_link, dealer_address, dealer_website_link, dealer_inventory_link, fb_link, insta_link, dealer_city, dealer_state, dealer_iframe_map, zip_code, latitude, longitude, full_address, detail_url, img_from_url, local_img_url, vehicle_make_id, title, year, make, model, vin, price, miles, type, modelNo, trim, stock, engine_details, transmission, body_description, fuel, drive_info, mpg, mpg_city, mpg_highway, exterior_color, interior_color, star, created_date, deal_review_number)
                               
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    
                ''', (dealer_id, deal_id, dealer_name, dealer_phone, dealer_description, dealer_additional_description, dealer_img_link, dealer_local_img_link , dealer_address, dealer_website_link, dealer_inventory_link, fb_link, insta_link, detail_city, detail_state, dealer_iframe_map, zip_code, latitude, longitude, full_address, link, detail_dealer_images, local_image_path, vehicle_make_id, detail_title, section_year, section_make, section_model, section_vin, detail_price, main_mileage, section_condition, modelNo, section_trim, section_stock, section_engine, section_transmission, section_body_type, section_fuel_type, main_drivetrain, section_city_gas_mileage, main_mpg, section_highway_gas_mileage, main_exterior_color, section_interiror_color, review_rate, formatted_time, review_number))
                conn.commit()

                csv_writers[5].writerow([dealer_id, deal_id, dealer_name, dealer_phone, dealer_description, dealer_additional_description, dealer_img_link, dealer_local_img_link ,detail_dealer_address, dealer_website_link, dealer_inventory_link, fb_link, insta_link, detail_city, detail_state, dealer_iframe_map, zip_code, latitude, longitude, full_address, link, detail_dealer_images, local_image_path, vehicle_make_id, detail_title, section_year, section_make, section_model, section_vin, detail_price, main_mileage, section_condition, modelNo, section_trim, section_stock, section_engine, section_transmission, section_body_type, section_fuel_type, main_drivetrain, section_city_gas_mileage, main_mpg, section_highway_gas_mileage, main_exterior_color, section_interiror_color, review_rate, formatted_time, review_number])


            # Print the scraped data
            print("Title:", detail_title)
            print("Price:", detail_price)
            print("Address:", detail_address_city_state)
            print("Dealer Review:", deal_review)
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


def extract_vehicle_info(URL, driver, conn, cursor, csv_writers, all_data, header_data, status=None):
    inventories_count = 0
    if URL:
        base_url = "https://www.cargurus.com"
        target_url = base_url + URL
        driver.execute_script("window.open(arguments[0], '_blank');", target_url)
        if status !='next':
            driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab

    try:
        # Wait for the main element to load
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//main[@id="main"]'))
        )
        
        # Extract dealer information
        dealer_info = data.find_element(By.XPATH, '//div[@class="dealerDetailsHeader"]//h1').text
        parts = dealer_info.split('-')
        dealer_name = parts[0].strip() if parts[0].strip() else 'N/A'

        
        dealer_inventory_count = parts[1].strip() if len(parts) > 1 else '0'
        dealer_inventory_count = dealer_inventory_count.replace(' Cars for Sale', '')

        dealer_address = data.find_element(By.XPATH, '//div[@class="dealerDetailsInfo"]').text

        address_cleaned = dealer_address.split('Map & directions')[0].strip()
        zip_code_match = re.search(r'\b\d{5}\b', address_cleaned)
        zip_code = zip_code_match.group(0) if zip_code_match else None
        
        # Locate the inventory section
        inventory_obj = data.find_element(By.XPATH, '//div[@class="fzhq3E"]')
        single_vehicle_rows = inventory_obj.find_elements(By.XPATH, '//div[@class="pazLTN"]')


        for idx, vehicle_row in enumerate(single_vehicle_rows):

            # Safe extraction for href
            vehicle_type_elems = vehicle_row.find_elements(By.XPATH, './/div[@data-testid="srp-tile-eyebrow"]//span')
            vehicle_type_text = " ".join([elem.text for elem in vehicle_type_elems]) if vehicle_type_elems else "N/A"

            vehicle_type_result = None
            if vehicle_type_elems:
                vehicle_type_vallidation = vehicle_type_text.lower()

                if vehicle_type_vallidation == 'new car':
                    vehicle_type_result = 'New'

                elif 'certified' in vehicle_type_vallidation:
                    vehicle_type_result = 'preowned certified'

                else:
                    vehicle_type_result = 'Used'
            else:
                    vehicle_type_result = 'Used'



            a_elems = vehicle_row.find_elements(By.XPATH, './/a[@data-testid="car-blade-link"]')
            a_href = a_elems[0].get_attribute('href') if a_elems else "N/A"

            # Safe extraction for status
            status_elems = vehicle_row.find_elements(By.XPATH, './/section[@role="contentinfo"]//span')
            status_text = status_elems[0].text if status_elems else "N/A"

            # Safe extraction for title
            title_elems = vehicle_row.find_elements(By.XPATH, './/h4[@data-cg-ft="srp-listing-blade-title"]')
            title = title_elems[0].text if title_elems else "N/A"

            # Safe extraction for mileage
            mileage_elems = vehicle_row.find_elements(By.XPATH, './/p[@data-testid="srp-tile-mileage"]')
            mileage = mileage_elems[0].text if mileage_elems else "N/A"

            cus_mileage = 0
            if mileage != 0:
                cus_mileage = re.sub(r'[\$,]', '', mileage)

            # Safe extraction for engine
            engine_elems = vehicle_row.find_elements(By.XPATH, './/p[@data-testid="seo-srp-tile-engine-display-name"]')
            engine = engine_elems[0].text if engine_elems else "N/A"

            # Safe extraction for price
            price_elems = vehicle_row.find_elements(By.XPATH, './/h4[@data-testid="srp-tile-price"]')
            price = price_elems[0].text if price_elems else 0

            cus_price = 0
            if price != 0:
                cus_price = re.sub(r'[\$,]', '', price)

            # Safe extraction for payment
            payment_elems = vehicle_row.find_elements(By.XPATH, './/span[@class="_monthlyPaymentText_noan4_230"]')
            payment = payment_elems[0].text if payment_elems else 0

            cus_payment = 0
            if payment != 0:
                cus_payment = re.sub(r'\D', '', payment)

            # Safe extraction for description
            description_elems = vehicle_row.find_elements(By.XPATH, './/div[@class="_text_1ncld_1"]')
            description = description_elems[0].text if description_elems else "N/A"

            # Safe extraction for phone
            phone_elems = vehicle_row.find_elements(By.XPATH, './/button[@data-testid="button-phone-number"]')
            phone = phone_elems[0].text if phone_elems else "N/A"

            cus_phone = "N/A"
            if phone != "N/A":
                cus_phone = re.sub(r'\D', '', phone)

            # Safe extraction for location
            location_elems = vehicle_row.find_elements(By.XPATH, './/div[@data-testid="srp-tile-bucket-text"]')
            if location_elems:
                location = location_elems[0].text
                city, state = location.split(',')[0].strip(), location.split(',')[1].strip()
            else:
                location, city, state = "N/A", "N/A", "N/A"

            button = vehicle_row.find_element(By.XPATH, './/div[@data-testid="srp-tile-bucket"]//button')
            button.click()


            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[@class='RQOhm']"))
            # )
            # modal_data = vehicle_row.find_element(By.XPATH, "//div[@role='dialog']//div[@class='RQOhm']")

            modal_data = vehicle_row.find_element(By.XPATH, "//div[@role='dialog']")
            feature_model_element = modal_data.find_element(By.XPATH, "//div[@class='_modalWrapper_1bypy_1']//ul[@class='_statsList_rlq8o_1']")
            feature_model_elements = feature_model_element.find_elements(By.XPATH, "//li[@class='_listItem_1tanl_14']")

            modal_row_all = {}
            for modal_row in feature_model_elements:
                # print(modal_row)
                modal_key = modal_row.find_element(By.XPATH, ".//h5").text
                modal_value = modal_row.find_element(By.XPATH, ".//p").text
                modal_row_all[modal_key] = modal_value


            feature_additional_model_element = modal_data.find_elements(By.XPATH, "//div[@class='_statsList_9o1ka_13']//div")
            if feature_additional_model_element:
                for additional_modal_row in feature_additional_model_element:
                    # print(additional_modal_row)
                    additional_modal_key = additional_modal_row.find_element(By.XPATH, ".//h4").text
                    additional_modal_value = additional_modal_row.find_element(By.XPATH, ".//span").text
                    modal_row_all[additional_modal_key] = additional_modal_value

            mileage = modal_row_all.get('Mileage', 'N/A')
            drivetrain = modal_row_all.get('Drivetrain', 'N/A')
            exterior_color = modal_row_all.get('Exterior color', 'N/A')
            interior_color = modal_row_all.get('Interior color', 'N/A')
            mpg = modal_row_all.get('MPG', 'N/A')
            engine = modal_row_all.get('Engine', 'N/A')
            fuel_type = modal_row_all.get('Fuel type', 'N/A')
            transmission = modal_row_all.get('Transmission', 'N/A')
            make = modal_row_all.get('Make:', 'N/A')
            model = modal_row_all.get('Model:', 'N/A')
            year = modal_row_all.get('Year:', 'N/A')
            trim = modal_row_all.get('Trim:', 'N/A')
            body_type = modal_row_all.get('Body type:', 'N/A')
            stock_number = modal_row_all.get('Stock #:', 'no_stock')
            vin = modal_row_all.get('VIN:', 'N/A')
            cus_inventory_link = a_href if a_href else 'N/A'
            
            # IMAGE DOWNLOAD START HEER 
            directory_location = 'uploads/single_image'
            vin_info = vin
            stock_info = stock_number

            replace_title_whitespace = title.replace(' ', '_').replace('/', '_').replace('-', '_')
            local_image_path = f"{directory_location}/{replace_title_whitespace + '_'+ vin_info + '_' +stock_info}.jpg"
            # --- Wait for the image to load ---
            try:
                # img_elem = vehicle_row.find_element(By.XPATH, './/img[@data-cg-ft="srp-listing-blade-image"]')
                # single_img_src = img_elem.get_attribute('src') if img_elem else "N/A"


                img_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/img[@data-cg-ft="srp-listing-blade-image"]'))
                ) 
                image_element = vehicle_row.find_element(By.XPATH, './/img[@data-cg-ft="srp-listing-blade-image"]')
                single_img_src = image_element.get_attribute('src') if image_element else "N/A"

                if single_img_src !="N/A":
                    image_name = "N/A"  
                    if '?' in single_img_src:
                        image_name = single_img_src.split('?')[0]
                    else:
                        image_name = single_img_src

                    print(f"Image src: {single_img_src}")
                    print(f"Image src: {image_name}")

                    if single_img_src != 'N/A':
                        download_image(image_name, directory_location, local_image_path)
            except Exception as e:
                    single_img_src = "Image not found"
                    print(f"Exception encountered: {e}")

            # Store the vehicle data
            result = {
                'Single Image': single_img_src,
                'Single Trim Image': image_name,
                'Dealer Name': dealer_name,
                'Dealer Address': dealer_address,
                'Inventory Link': cus_inventory_link,
                'Vehicle Type Short Info': vehicle_type_text,
                'Status': status_text,
                'Title': title,
                'Mileage': cus_mileage,
                'Drivetrain': drivetrain,
                'Exterior Color': exterior_color,
                'Interior Color': interior_color,
                'MPG': mpg,
                'Engine': engine,
                'Fuel Type': fuel_type,
                'Transmission': transmission,
                'Make': make,
                'Model': model,
                'Year': year,
                'Trim': trim,
                'Body Type': body_type,
                'Stock Number': stock_number,
                'Vin': vin,
                'Price': cus_price,
                'Payment': cus_payment,
                'Description': description,
                'Phone': cus_phone,
                'Location': location
            }

            all_data.append(result)

            close_button = vehicle_row.find_element(By.XPATH, "//button[@aria-label='Close dialog']")
            close_button.click()

            print(modal_row_all)
            print(result)
            print('*'*30 )
            print('*'*30 )
            print('*'*30 )


            # existing_dealer_id = get_existing_dealer_id(cursor, dealer_name, full_address, zip_code)
            # if existing_dealer_id:
            #     dealer_id = existing_dealer_id  # Use existing dealer ID
            # else:
            #     dealer_id = get_new_dealer_id(cursor) 
            ## Scroll down the page
            scroll_down_slowly(driver)


            time.sleep(5)

            # Insert into SQLite
            created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dealer_id = 'CG-241000'
            vehicle_id = 'C-241000'
            dealer_iframe_map = None
            deal_rating = None
            model_no = None
            driveInfo = None
            mpg_city =None
            mpg_highway =None
            star = None
            batch_no  = 1
            in_market= None
            
            cursor.execute('''
                INSERT INTO vehicles (dealer_id, dealer_name, phone, description, dealer_address, city, state, dealer_iframe_map, zip_code, a_href, 
                                    single_img_src, local_image_path, title, year, make, model, vin, price, mileage, vehicle_type, 
                                    model_no, trim, stock_number, engine, transmission, body_type, fuel_type, driveInfo, mpg_city, mpg_highway, 
                                    exterior_color, star, created_date, batch_no, cus_inventory_link, payment, in_market, mpg, interior_color, drivetrain, 
                                    status_text, dealer_inventory_count, vehicle_type_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dealer_id, dealer_name, cus_phone, description, dealer_address, city, state, dealer_iframe_map, zip_code, a_href, 
                single_img_src, local_image_path, title, year, make, model, vin, cus_price, cus_mileage, vehicle_type_result, 
                model_no, trim, stock_number, engine, transmission, body_type, fuel_type, driveInfo, mpg_city, mpg_highway, 
                exterior_color, star, created_date, batch_no, cus_inventory_link, cus_payment, in_market, mpg, interior_color, drivetrain, 
                status_text, dealer_inventory_count, vehicle_type_text))
            conn.commit()

            # Write to dealers CSV
            csv_writers[3].writerow([dealer_id, dealer_name, cus_phone, description, dealer_address, city, state, dealer_iframe_map, zip_code, a_href, 
                single_img_src, local_image_path, title, year, make, model, vin, cus_price, cus_mileage, vehicle_type_result, 
                model_no, trim, stock_number, engine, transmission, body_type, fuel_type, driveInfo, mpg_city, mpg_highway, 
                exterior_color, star, created_date, batch_no, cus_inventory_link, cus_payment, in_market, mpg, interior_color, drivetrain, 
                status_text, dealer_inventory_count, vehicle_type_text ])

        print('Vehicle single data saved in DB and CSV!')

        ## Paginate through multiple pages
        number_of_pages = 3
        for page in range(number_of_pages - 1):
            logging.info(f"Currently on page {page + 1}")
            if not navigate_to_next_page(driver, page, conn, cursor, csv_writers, all_data, header_data):
                logging.info("No more pages to navigate or encountered an error.")
                break
            # extract_vehicle_info(None, driver, conn, cursor, csv_writers, all_data, header_data)

    except Exception as e:
        logging.error(f"Error occurred while extracting vehicle information: {e}")

    finally:
        driver.close()
        # driver.switch_to.window(driver.window_handles[0])
        driver.switch_to.window(driver.window_handles[0]) if len(driver.window_handles) > 1 else driver.quit()

    return dealer_name, dealer_address




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
        
        
        local_image_path = ''
        if img_src != 'No image':
            
            directory_location = 'public/uploads/dealer'

            # Check if the directory exists, and create it only if it doesn't
            if not os.path.exists(directory_location):
                os.makedirs(directory_location)
                print(f"Directory created: {directory_location}")
            else:
                print(f"Directory already exists: {directory_location}")

            location_url = f"{city} _ {state}" if zip_code else 'default_location'
            cus_dealer_name = re.sub(r'\s+', '-', name)
            detail_local_image_path = f"{directory_location}/{cus_dealer_name}_{city}_{state}.jpg"
            local_image_path =  detail_local_image_path
            download_image(img_src, directory_location, local_image_path)

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
            'local_img' : local_image_path,
            'Radius' : radius,
            'Rating' : rating,
            'Review Count' : review_count_only,
            'View inventory' : inventory_link_cus,
        }

        single_all_data.append(information)
        
        # Scroll down the page
        scroll_down_slowly(driver)
        
        # time.sleep
        # dealer_id = "D-24770071"
        batch = 1
        status = 1
        # Insert into SQLite

        cursor.execute('''
            INSERT INTO dealers (dealer_id,name, phone, address, city, state, dealer_full_address, dealer_iframe_map, zip, about_me, img, local_img, radius, rating, review_count_only, inventory_link, batch, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dealer_id, name, phone, address, city, state, address_cus, dealer_iframe_map, zip_code, review_text, img_src, local_image_path, radius, rating, review_count_only, inventory_link_cus, batch, status))
        conn.commit()

        # Write to dealers CSV
        dealer_csv_writer[1].writerow([dealer_id, name, phone, full_address, city, state, address_cus, dealer_iframe_map, zip_code, review_text, img_src, local_image_path, radius, rating, review_count_only, inventory_link_cus, batch, status ])

        print("*"*50)
        print(information)
        print('Dealer data saved in data sqlite and csv')
        print("*"*50)

        # dealer_data = []
        # single_name, single_address = extract_vehicle_info(inventory_link, driver, conn, cursor, dealer_csv_writer, dealer_data, HEADER)

        # single_all_data.append(dealer_data)

    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])
    return single_all_data


def csv_reader():
    dealers_data = []
    csv_file_path = 'public/dealerProcess/houston_dealers_info.csv'
    # Open the CSV file and read its contents
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # Append each row as a dictionary to the list
            dealers_data.append(row)
    
    # for dealer in dealers_data:
    #     print("Invnetory Link:", dealer['Invnetory Link'])

    return dealers_data


def main2():
    # Set up logging (optional)
    logging.basicConfig(level=logging.INFO)

    # zip_code_input_data = initial_zip_code_seter()

    # conn, cursor, dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer, inventory_details_csv_file, inventory_details_csv_writer  = setup_db_and_csv(zip_code_input_data)
    # conn, cursor, dealer_csv_file, dealer_csv_writer  = setup_db_and_csv()

    main_driver = initialize_webdriver()
    # targated_url = custom_url()

    # URL = targated_url
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    # logging.info(URL)
    # main_driver.get(URL)

    # driver = WebDriverWait(main_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="addressTyped"]')))



    logging.info("Clicked the submit button")

    # single_all_data = []
    # extract_dealer_info(main_driver, conn, cursor, (dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer, inventory_details_csv_file, inventory_details_csv_writer), single_all_data, HEADER)

    # # Loop through pages
    # number_of_pages = 15
    # for page in range(1, number_of_pages):
    #     if not navigate_to_next_dealer_page(main_driver, page):
    #         break
    #     extract_dealer_info(main_driver, conn, cursor, (dealer_csv_file, dealer_csv_writer, inventory_csv_file, inventory_csv_writer, inventory_details_csv_file,inventory_details_csv_writer ), single_all_data, HEADER)

    # print(single_all_data)
    print('*'*40)
    time.sleep(10)
    main_driver.quit()

    # dealer_csv_file.close()   
    # inventory_csv_file.close()
    # inventory_details_csv_file.close()

    # Clean up: Close the database connection
    # conn.close()
    
def main():
    csv_link = csv_reader()
    print(csv_link)
    for dealer in csv_link:
        print("Invnetory Link:", dealer['Invnetory Link'])


if __name__ == "__main__":
    main()