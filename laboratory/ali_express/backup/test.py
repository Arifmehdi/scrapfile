from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from tkinter import messagebox
from datetime import datetime
import tkinter as tk
import threading
import requests
import logging
import sys
import os
import time
import csv


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
        time.sleep(30)
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





# Scraping function
def scrape_aliexpress(url):
    driver = initialize_webdriver()  # Use your existing WebDriver initialization
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(url)
    driver.get(url)
    logging.info("Waiting for the page to load")

    all_data = []
    data = extract_vehicle_info(url, driver, all_data, HEADER)  # Your existing scraping logic
    print(data)
    driver.quit()
    return all_data 

def scrape_in_thread():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Input Error", "Please enter a valid URL")
        return

    # Start the scraping process in a separate thread
    scrape_thread = threading.Thread(target=scrape_and_show, args=(url,))
    scrape_thread.start()

# GUI setup
def scrape_and_show(url):
    result_text.delete(1.0, tk.END)  # Clear the text area

    # Call the scraping function and get the data
    all_data = scrape_aliexpress(url)

    # Format the scraped data for display
    if all_data:
        for product in all_data:
            product_info = (
                f"Title: {product['Title']}\n"
                f"Current Price: {product['Current Price']}\n"
                f"Original Price: {product['Original Price']}\n"
                f"Discount: {product['Discount']}\n"
                f"Rating: {product['Rating']}\n"
                f"Reviews: {product['Reviews']}\n"
                f"Sold Count: {product['Sold Count']}\n"
                f"Color Text: {product['Color Text']}\n"
                "-----------------------------\n"
            )
            result_text.insert(tk.END, product_info)  # Insert each product's info into the text area
    else:
        result_text.insert(tk.END, "No data found or an error occurred.")

    # result = scrape_aliexpress(url)
    # result_text.delete(1.0, tk.END)
    # result_text.insert(tk.END, result)


root = tk.Tk()
root.title("AliExpress Scraper")
root.geometry("500x400")

# URL input
tk.Label(root, text="Enter AliExpress Product URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Scrape button
scrape_button = tk.Button(root, text="Scrape Data", command=scrape_and_show)
scrape_button.pack(pady=10)

# Display result
result_text = tk.Text(root, height=15, width=60)
result_text.pack(pady=20)

# Start GUI loop
root.mainloop()
