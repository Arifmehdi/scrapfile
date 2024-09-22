from selenium import webdriver
from selenium.webdriver.common.by import By
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
import os
import time
import csv
import logging
import sys

import re
from mysql_connector import get_mysql_connection


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
    base_url = "https://driverbase.com/"
    addition_url = "inventory/location/"
    # location_url  = "houston-tx"
    location_url  = "sanantonio-tx"
    targated_url  = base_url+addition_url+location_url

    return targated_url

def navigate_to_next_page(driver, page_number):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Next"]'))
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

#     # remote_image_url,local_directory,local_image_path
# def download_image(remote_url, directory_location, local_image_path):

#     # Replace whitespaces in single_title with underscores

#     # Create the directory if it doesn't exist
#     if not os.path.exists(directory_location):
#         os.makedirs(directory_location)
        
#     response = requests.get(remote_url)
#     if response.status_code == 200:
#         with open(local_image_path, 'wb') as file:
#             file.write(response.content)
#         print(f"Image downloaded successfully to {local_image_path}")
#     else:
#         print(f"Failed to download image from {remote_url}. Status code: {response.status_code}")



def extract_vehicle_info(URL, driver, all_data, header_data):

    try:
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//table[@id="inventory_vehicles_table"]'))
        )
    except AttributeError as e :
        logging.error("Timeout waiting for page to load: %s", e)
        driver.quit()
        sys.exit(1)

    logging.info("Fetching webpage content with requests")
    try:
        address_obj = data.find_element(By.XPATH,"//form[@id='vlp_form']//div//h1").text
        custom_address_obj = address_obj.replace('Cars for Sale Near ','')
        custom_addrtess_split = custom_address_obj.split(',')
        custom_city = custom_addrtess_split[0]
        custom_state = custom_addrtess_split[1].replace(' ', '')
        zip_obj = data.find_element(By.XPATH,"//form[@id='vlp_form']//input[@id='select_zip']").get_attribute('value')

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

        inventories_count = 0
        for row in rows:
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

            details_data = row.find_all('small')
            vin = stock = mpg_city = mpg_highway = engine = transmission = "Not found"
            for detail in details_data:
                detail_text = detail.text.strip()
                
                # VIN
                if detail_text.startswith("VIN"):
                    vin = detail_text
                
                # Stock
                elif detail_text.startswith("Stock"):
                    stock = detail_text
                
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
            # --- Wait for the image to load ---
            try:
                # Explicitly wait for the image to have a `src` attribute
                image_tag = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//img[@class='lazy']"))
                ) 
                image_src = image_tag.get_attribute('src') if image_tag else "Image not found"
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

            inventories_count += 1 

            # Click the link to open the details page
            driver.execute_script("window.open(arguments[0], '_blank');", link)
            driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab

            # Wait for the detail page to load and scrape data (add your detailed page scraping logic here)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@id='content']")))
                # Add your scraping logic here for the detailed page

                # Example: Scrape more data from the detailed page
                detail_title = driver.find_element(By.XPATH, "//header//div//div[2]//div[2]//h1").text  
                detail_price = driver.find_element(By.XPATH, "//header//div//div[2]//div[2]//h3").text  
                # detail_monthly_pay = driver.find_element(By.XPATH, "//span[@id='pmt']").text  

                detail_status_span = row.find_all('span')
                detail_possible_statuses = ["New", "Preowned", "Certified Preowned"]
                detail_status = "Not Found"
                for detail_span in detail_status_span:
                    detail_span_text = detail_span.text.strip()
                    if detail_span_text in detail_possible_statuses:
                        detail_status = detail_span_text

                        parent_text = detail_span.find_parent('span').text.strip()
                        detail_engine = parent_text.replace(detail_status, '').strip()
                        break

                print(f"Detail Title: {detail_title}")
                print(f"Detail Price: {detail_price}")
                print(f"Detail Status: {detail_status}")
                print(f"Detail Engine: {detail_engine}")
                # print(f"Detail Monthly payment: {detail_monthly_pay}")

            except Exception as e:
                print(f"Error fetching details from the page: {e}")
            
            # Close the detail tab and switch back to the main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            print(f"Link: {link}")
            print(f"Custom Link: {cus_link}")
            print(f"Vehicle: {vehicle_name}")
            print(f"Status: {status}")
            print(f"Price: {price}")
            print(f"Details: {', '.join(details)}")

            print(f"VIN: {vin}")
            print(f"Stock: {stock}")
            print(f"MPG City: {mpg_city}")
            print(f"MPG Highway: {mpg_highway}")
            print(f"Engine: {engine}")
            print(f"Transmission: {transmission}")
            print(f"Image URL: {image_src}")
            print(f"Dealer Link: {dealer_href}")
            print(f"Dealer Text: {dealer_text}")
            print(f"Days on Driverbase: {days_text}")
            print(f"Views: {views_text}")
            print(f"Count: {inventories_count}")
            print("\n")
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(5)

        print(address_obj)
        print(zip_obj)
        print(custom_address_obj)
        print(custom_city)
        print(custom_state)
        print(f"total Count: {inventories_count}")


        # sys.exit()

    except AttributeError:
        links = ''


def main():
    # url_input = input('Write or Paste your URL : ')
    driver = initialize_webdriver()
    targated_url = custom_url()

    URL = targated_url
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(URL)
    driver.get(URL)
    logging.info("Waiting for the page to load")

    all_data = []
    data = extract_vehicle_info(URL,driver, all_data, HEADER)

    number_of_pages = 1
    for page in range(number_of_pages - 1):
        if not navigate_to_next_page(driver, page):
            break
        extract_vehicle_info(URL, driver, all_data, HEADER)

    
    # print(d)
    driver.quit()

if __name__ == "__main__":
    main()