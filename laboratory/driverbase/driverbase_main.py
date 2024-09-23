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
    # location_url  = "sanantonio-tx"
    location_url  = "dallas-tx"
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



def extract_vehicle_info(URL, driver, all_data, header_data):
    inventories_count = 0 
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

            replace_title_whitespace = single_title.replace(' ', '_').replace('/', '_')
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


        #    ************************************* detail page start here ******************************
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

                detail_dealer_href = base_url + detail_dealer_link_tag.get_attribute('href') if detail_dealer_link_tag else "Dealer link not found"
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
                
                try:
                    img_stack = driver.find_element(By.XPATH, '//img[@src="/public/img/icn/img-stack.png"]')
                    img_stack_src = img_stack.get_attribute('src')
                    print(f"Image stack src: {img_stack_src}")
                    sibling_images = img_stack.find_elements(By.XPATH, '../../following-sibling::div//img')
                    sibling_image_sources = [img.get_attribute('src') for img in sibling_images]
                    image_sources_str = ",".join(sibling_image_sources)

                    # Print all sibling image sources found
                    downloaded_image_paths = []
                    for idx, img_src in enumerate(sibling_image_sources[:5], 1):
                        location_url = URL.split('/')[-1]
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

                print(f"Detail Title: {detail_title}")
                print(f"Detail Price: {detail_price}")
                print(f"Detail Status: {detail_status}")
                print(f"Detail Engine: {detail_engine}")
                print(f"Detail Monthly payment: {detail_monthly_pay}")
                print(f"Detail Dealer href: {detail_dealer_href}")
                print(f"Detail Dealer text: {detail_dealer_text}")
                print(f"Detail Dealer Phone: {detail_dealer_phone}")
                print(f"Detail Days Text: {detail_days_text}")
                print(f"Detail Views Text: {detail_views_text}")
                print(f"Detail Web Link: {detail_dealer_web_link}")
                print(f"Detail dealer Name: {detail_dealer_name_text}")
                print(f"Detail dealer Comment: {detail_dealer_comment}")
                print(f"Detail Image Link: {image_sources_str}")
                time.sleep(3)

            except Exception as e:
                print(f"Error fetching details from the page: {e}")
            
            # Close the detail tab and switch back to the main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        #    ************************************* detail page end here ******************************

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
            print(f"Single local image path : {local_image_path}")
            print(f"Detail 5 local image : {downloaded_image_paths}")
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

    number_of_pages = 3
    for page in range(number_of_pages - 1):
        if not navigate_to_next_page(driver, page):
            break
        extract_vehicle_info(URL, driver, all_data, HEADER)

    
    # print(d)
    driver.quit()

if __name__ == "__main__":
    main()