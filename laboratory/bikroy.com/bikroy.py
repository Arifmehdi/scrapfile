import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import random # Import random for delays
import csv # Import csv for CSV output

def initialize_selenium():
    """
    Initializes Selenium WebDriver and returns the driver object.
    """
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    return driver

def fetch_html_with_selenium(driver, url):
    """
    Uses Selenium to fetch the given URL and returns the HTML content.
    """
    driver.get(url)
    time.sleep(random.uniform(3, 7)) # Random delay to avoid detection
    return driver.page_source

def parse_and_extract_data(html_content, output_file):
    """
    Parses the HTML content to extract ad data and appends it to a JSON file.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    ads = soup.find_all('li', class_='normal--2QYVk')

    print(f"Found {len(ads)} ads on this page.")

    all_ads_data = []
    for ad in ads:
        title_element = ad.find('a', class_='gtm-ad-item')
        price_element = ad.find('div', class_='price--3SnqI')
        location_element = ad.find('div', class_='description--2-ez3')
        update_time = ad.find('div', class_="updated-time--1DbCk")

        title = title_element.get('title').replace(" for sale", "") if title_element else "N/A"
        price = price_element.text.strip() if price_element else "N/A"
        detail_link = title_element.get('href') if title_element else "N/A"

        location = "N/A"
        if location_element:
            location_text = location_element.get_text(separator=" ", strip=True)
            location = re.sub(r'\d+\s*(days|hours|minutes|seconds)\s*ago', '', location_text, flags=re.IGNORECASE).strip()
            location = re.sub(r'\d+\s*(days|hours|minutes|seconds)', '', location, flags=re.IGNORECASE).strip()
            location = re.sub(r'(Today|Yesterday)', '', location, flags=re.IGNORECASE).strip()
            location = re.sub(r'\s+', ' ', location).strip()
            if not location:
                location = "N/A"
        address = location.split(',')[0].strip()

        ad_data = {
            "title": title,
            "price": price,
            "location": location,
            "address" : address,
            "detail_link": detail_link
        }
        
        updated_time_element = ad.find('span', class_='bump-up-time--Z8zuY')
        updated_time = updated_time_element.text.strip() if updated_time_element else "N/A"
        ad_data["updated_time"] = updated_time
        all_ads_data.append(ad_data)

    # Load existing data if file exists, then append new data
    try:
        with open(output_file, "r+", encoding="utf-8") as f:
            file_content = f.read()
            if file_content:
                existing_data = json.loads(file_content)
                existing_data.extend(all_ads_data)
                f.seek(0)
                f.truncate()
                json.dump(existing_data, f, indent=4)
            else:
                json.dump(all_ads_data, f, indent=4)
    except FileNotFoundError:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_ads_data, f, indent=4)

    print(f"Appended {len(all_ads_data)} ads to {output_file}")

def save_to_csv(json_file_path, csv_file_path):
    """
    Reads data from a JSON file and writes it to a CSV file.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return

    if not data:
        print("No data to write to CSV.")
        return

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)
    print(f"Successfully saved data to CSV: {csv_file_path}")

def main():
    output_json_path = r"C:\laragon\www\scrapfile\laboratory\bikroy.com\bikroy_ads.json"
    base_url = "https://bikroy.com/en/ads?query=camera"
    driver = None
    try:
        driver = initialize_selenium()
        current_page = 1
        while True:
            print(f"\nStep 1: Fetching HTML using Selenium for page {current_page}...")
            url = f"{base_url}&page={current_page}" if current_page > 1 else base_url
            html_content = fetch_html_with_selenium(driver, url)

            print(f"Step 2: Parsing HTML and extracting ad data from page {current_page}...")
            parse_and_extract_data(html_content, output_json_path)

            # Check for the "Next" button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.nextButton--25Tal a"))
                )
                # Check if the next button is disabled or if it's the last page
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to scrape. Exiting.")
                    break
                next_button.click()
                current_page += 1
                time.sleep(random.uniform(5, 10)) # Longer random delay between page navigations
            except Exception as e:
                print(f"Could not find or click the 'Next' button, or it was the last page: {e}")
                break
    # print("Scraping complete.")
            save_to_csv(output_json_path, output_json_path.replace(".json", ".csv"))
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()