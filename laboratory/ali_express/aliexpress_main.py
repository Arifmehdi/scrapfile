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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_title(soup):
    try:
        title = soup.find('span', attrs={'id': 'productTitle'})
        title_value = title.text
        title_string = title_value.strip()
    except AttributeError:
        title_string = ''
    return title_string

def get_price(soup):
    try:
        price = soup.find('span', attrs={'class': 'a-price a-text-price a-size-medium apexPriceToPay'})
        title_value = price.string.strip()
        price = title_value.strip()
    except AttributeError:
        price = ''
    return price

def get_rating_count(soup):
    try:
        rating = soup.find('span', attrs={'class': 'a-size-base a-color-base'})
        rating_value = rating.string.strip()
    except AttributeError:
        try:
            rating = soup.find('span', attrs={'class': 'a-icon-alt'}).string.strip()
        except AttributeError:
            rating = ''
    return rating

def navigate_to_next_page(driver, page_number):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[text()="Next"]'))
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

def scrape_product_data(driver, url, HEADER):
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//span[(@id, "productTitle")]'))
    )
    time.sleep(3)
    webpage = requests.get(url, headers=HEADER)
    content = webpage.content
    soup = BeautifulSoup(content, 'html.parser')
    title = get_title(soup)
    price = get_price(soup)
    rating = get_rating_count(soup)
    return title, price, rating


def row_exists(row, existing_data):
    for existing_row in existing_data:
        if all(row[key] == existing_row[key] for key in row):
            return True
    return False


def extract_vehicle_info(URL, driver, all_data, header_data):

    try:
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="root"]'))
        )
    except AttributeError as e :
        logging.error("Timeout waiting for page to load: %s", e)
        driver.quit()
        sys.exit(1)

    logging.info("Fetching webpage content with requests")
    try:

        html_content = data.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')

        file_path = 'upload/formatted_html.txt'

        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(soup.prettify())

            logging.info(f"HTML content saved to {file_path}")
        else:
            logging.info(f"{file_path} already exists. No file created.")


        # Extract the title # Extract current price # Extract original price and discount # Extract rating
        # Extract number of reviews # Extract sold count # Extract color text # Extract all images

        title = soup.find('h1', {'data-pl': 'product-title'}).text.strip()
        current_price = soup.find('span', class_='price--currentPriceText--V8_y_b5').text.strip()
        original_price = soup.find('span', class_='price--originalText--gxVO5_d').text.strip()
        discount = soup.find('span', class_='price--discount--Y9uG2LK').text.strip()
        rating = soup.find('strong').text.strip()
        reviews = soup.find('a', class_='reviewer--reviews--cx7Zs_V').text.strip()
        sold_count = soup.find('span', class_='reviewer--sold--ytPeoEy').text.strip()
        color_text = soup.find('div', class_='sku-item--title--Z0HLO87').text.strip()

        image_elements = soup.find_all('img')
        images = [img['src'] for img in image_elements if 'src' in img.attrs]

        # Print extracted information
        all_product_info = [{
            "Title": title,
            "Current Price": current_price,
            "Original Price": original_price,
            "Discount": discount,
            "Rating": rating,
            "Reviews": reviews,
            "Sold Count": sold_count,
            "Color Text": color_text,
        }]

        # # Print extracted information
        # for key, value in all_product_info.items():
        #     print(f"{key}: {value}")

        clickable_images = driver.find_elements(By.XPATH, '//div[@class="sku-item--image--jMUnnGA"]')
        # print(clickable_images)
        # sys.exit()
        for index, image in enumerate(clickable_images):

            driver.execute_script("arguments[0].scrollIntoView(true);", image)
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(image)).click()
                print(f"Clicked on image {index + 1}")
            except ElementClickInterceptedException:
                print(f"Retry clicking on image {index + 1} with JavaScript")
                driver.execute_script("arguments[0].click();", image)
                # print(f"Retry clicking on image {index + 1}")
                # driver.execute_script("arguments[0].click();", image) 

            # image.click()
            time.sleep(2)
            print(f"Clicking on image {index + 1}")

            updated_html_content = driver.page_source
            updated_soup = BeautifulSoup(updated_html_content, 'html.parser')

            updated_current_price = updated_soup.find('span', class_='price--currentPriceText--V8_y_b5').text.strip()
            updated_original_price = updated_soup.find('span', class_='price--originalText--gxVO5_d').text.strip()
            updated_discount = updated_soup.find('span', class_='price--discount--Y9uG2LK').text.strip()
            updated_color_text = updated_soup.find('div', class_='sku-item--title--Z0HLO87').text.strip()

                        # Add the updated data to the list
            all_product_info.append({
                "Title": title,
                "Current Price": updated_current_price,
                "Original Price": updated_original_price,
                "Discount": updated_discount,
                "Rating": rating,
                "Reviews": reviews,
                "Sold Count": sold_count,
                "Color Text": updated_color_text,
            })
            time.sleep(2)


            cus_name = datetime.now().strftime('%Y%m%d_') + 'vehicle_info.csv'
            csv_file_path = 'upload/' + cus_name
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

            existing_data = []
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    existing_data = list(reader)

            # Save the data to the CSV file, avoiding duplicates
            keys = all_product_info[0].keys()

            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)

                # Write the header only if the file is being created
                if not os.path.exists(csv_file_path) or os.stat(csv_file_path).st_size == 0:
                    writer.writeheader()

                for row in all_product_info:
                    if not row_exists(row, existing_data):
                        writer.writerow(row)


            # # Save the data to a CSV file
            # cus_name = datetime.now().strftime('%Y%m%d_') + 'vehicle_info.csv'
            # csv_file_path = 'upload/' + cus_name
            # os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

            # file_exists = os.path.isfile(csv_file_path)
            # keys = all_product_info[0].keys()

            # with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            #     writer = csv.DictWriter(csvfile, fieldnames=keys)

            #     if not file_exists:
            #         writer.writeheader()
                
            #     writer.writerows(all_product_info)

            print(f"Vehicle information saved to {csv_file_path}")

            print(f"\nUpdated Data for Image {index + 1}:")
            print("-" * 40)
            print("Updated Title:", title)
            print("Updated Current Price:", updated_current_price)
            print("Updated Original Price:", updated_original_price)
            print("Updated Discount:", updated_discount)
            print("Updated Rating:", rating)
            print("Updated Reviews:", reviews)
            print("Updated Sold Count:", sold_count)
            print("Updated Color Text:", updated_color_text)
            print("-" * 40)

        print("Result here ")
        print(all_product_info)
        sys.exit()

    except AttributeError:
        links = ''



def main():
    url_input = input('Write or Paste your URL : ')
    driver = initialize_webdriver()
    # URL = "https://www.aliexpress.us/item/3256807098852847.html?spm=a2g0o.home.pcJustForYou.1.650c76db8SxNPQ&gps-id=pcJustForYou&scm=1007.13562.333647.0&scm_id=1007.13562.333647.0&scm-url=1007.13562.333647.0&pvid=3aebee93-4730-4820-88e3-faac6f53517c&_t=gps-id%3ApcJustForYou%2Cscm-url%3A1007.13562.333647.0%2Cpvid%3A3aebee93-4730-4820-88e3-faac6f53517c%2Ctpp_buckets%3A668%232846%238107%231934&isseo=y&pdp_npi=4%40dis%21EUR%213.82%210.91%21%21%214.18%211.00%21%402101eeda17246692310713965e5be4%2112000040070023678%21rec%21IE%21%21ABX&utparam-url=scene%3ApcJustForYou%7Cquery_from%3A&gatewayAdapt=4itemAdapt"
    # URL = "https://www.aliexpress.us/item/1005006341854760.html?spm=a2g0o.home.pcJustForYou.18.650c76db8SxNPQ&gps-id=pcJustForYou&scm=1007.32079.367808.0&scm_id=1007.32079.367808.0&scm-url=1007.32079.367808.0&pvid=956873b9-3d98-470a-b8eb-c8ef170bde0e&_t=gps-id%3ApcJustForYou%2Cscm-url%3A1007.32079.367808.0%2Cpvid%3A956873b9-3d98-470a-b8eb-c8ef170bde0e%2Ctpp_buckets%3A668%232846%238107%231934&isseo=y&pdp_npi=4%40dis%21EUR%2118.41%2118.23%21%21%2120.12%2119.92%21%402101eeda17246692310713965e5be4%2112000036823943557%21rec%21IE%21%21ABX&utparam-url=scene%3ApcJustForYou%7Cquery_from%3A&search_p4p_id=202408260347111025193960828235087328_2&_gl=1*1twioub*_gcl_au*NTk2OTIyODk1LjE3MjQ2NjkyMDY.*_ga*MTQyMDI5Mjg4NS4xNzI0NjY5MjA2*_ga_VED1YSGNC7*MTcyNDY2OTIwNi4xLjEuMTcyNDY2OTI5MC4zNi4&gatewayAdapt=4itemAdapt"
    # URL = "https://www.aliexpress.us/item/1005007518115265.html?spm=a2g0o.home.pcJustForYou.13.650c76db8SxNPQ&gps-id=pcJustForYou&scm=1007.13562.333647.0&scm_id=1007.13562.333647.0&scm-url=1007.13562.333647.0&pvid=3aebee93-4730-4820-88e3-faac6f53517c&_t=gps-id%3ApcJustForYou%2Cscm-url%3A1007.13562.333647.0%2Cpvid%3A3aebee93-4730-4820-88e3-faac6f53517c%2Ctpp_buckets%3A668%232846%238107%231934&isseo=y&pdp_npi=4%40dis%21EUR%2113.94%210.91%21%21%21108.39%217.08%21%402101eeda17246692310713965e5be4%2112000041101428097%21rec%21IE%21%21ABX&utparam-url=scene%3ApcJustForYou%7Cquery_from%3A&_gl=1*1twioub*_gcl_au*NTk2OTIyODk1LjE3MjQ2NjkyMDY.*_ga*MTQyMDI5Mjg4NS4xNzI0NjY5MjA2*_ga_VED1YSGNC7*MTcyNDY2OTIwNi4xLjEuMTcyNDY2OTI5MC4zNi4wLjA.&gatewayAdapt=4itemAdapt"
    URL = url_input
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(URL)
    driver.get(URL)
    logging.info("Waiting for the page to load")

    all_data = []
    data = extract_vehicle_info(URL,driver, all_data, HEADER)
    print(data )
    # sys.exit()

    # number_of_pages = 200
    # for page in range(number_of_pages - 1):
    #     if not navigate_to_next_page(driver, page):
    #         break
    #     extract_vehicle_info(driver, all_data)

    
    # print(d)
    driver.quit()

if __name__ == "__main__":
    main()
