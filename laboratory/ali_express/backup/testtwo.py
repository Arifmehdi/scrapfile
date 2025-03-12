import tkinter as tk
from tkinter import messagebox
import threading
import logging
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

# WebDriver initialization
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

# Function to extract vehicle information
def extract_vehicle_info(URL, driver, all_data, header_data):
    try:
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="root"]'))
        )
        time.sleep(30)
    except AttributeError as e:
        logging.error("Timeout waiting for page to load: %s", e)
        driver.quit()
        sys.exit(1)

    html_content = data.get_attribute('innerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Save HTML content to file
    file_path = 'upload/formatted_html.txt'
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())
        logging.info(f"HTML content saved to {file_path}")
    else:
        logging.info(f"{file_path} already exists. No file created.")

    # Extract data
    title = soup.find('h1', {'data-pl': 'product-title'}).text.strip()
    current_price = soup.find('span', class_='price--currentPriceText--V8_y_b5').text.strip()
    original_price = soup.find('span', class_='price--originalText--gxVO5_d').text.strip()
    discount = soup.find('span', class_='price--discount--Y9uG2LK').text.strip()
    rating = soup.find('strong').text.strip()
    reviews = soup.find('a', class_='reviewer--reviews--cx7Zs_V').text.strip()
    sold_count = soup.find('span', class_='reviewer--sold--ytPeoEy').text.strip()
    color_text = soup.find('div', class_='sku-item--title--Z0HLO87').text.strip()

    # Append extracted information
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
    
    # Add to final data
    all_data.extend(all_product_info)

    driver.quit()
    return all_data

# Scraping function
def scrape_aliexpress(url):
    driver = initialize_webdriver()
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(url)
    driver.get(url)
    logging.info("Waiting for the page to load")

    all_data = []
    extract_vehicle_info(url, driver, all_data, HEADER)
    
    return all_data

# Function to start scraping in a separate thread
def scrape_in_thread():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Input Error", "Please enter a valid URL")
        return

    # Start the scraping process in a separate thread
    scrape_thread = threading.Thread(target=scrape_and_show, args=(url,))
    scrape_thread.start()

# GUI callback to display scraped data
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

# GUI setup
root = tk.Tk()
root.title("AliExpress Scraper")
root.geometry("500x400")

# URL input
tk.Label(root, text="Enter AliExpress Product URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Scrape button
scrape_button = tk.Button(root, text="Scrape Data", command=scrape_in_thread)
scrape_button.pack(pady=10)

# Display result
result_text = tk.Text(root, height=15, width=60)
result_text.pack(pady=20)

# Start GUI loop
root.mainloop()
