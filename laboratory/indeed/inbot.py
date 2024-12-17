import os
import time
import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



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


        
def initial_profession_seter():
    # GUI for selecting profession
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    profession_choices = {
        1: 'web designer',
        2: 'web developer',
        3: 'graphic design',
        4: 'accountant',
        5: 'marketing manager',
        6: 'data entry',
        7: 'network engineer',
        8: 'supply chain',
        9: 'store manager',
        10: 'seo specialist'
    }

    options = "\n".join([f"[{key}] {value}" for key, value in profession_choices.items()])
    profession_input = simpledialog.askstring("Select Profession", f"Choose Your Profession:\n\n{options}")
    
    try:
        profession_input = int(profession_input)
        if profession_input in profession_choices:
            professional_input_data = profession_choices[profession_input]
        else:
            raise ValueError
    except (ValueError, TypeError):
        professional_input_data = ''  # Default to empty if input is invalid or canceled

    print(f"Selected profession is: {professional_input_data}")
    return professional_input_data


def initial_location_seter():
    # GUI for selecting location
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    location_choices = {
        1: 'United States',
        2: 'Russia, NJ',
        3: 'Houston, TX',
        4: 'Canada, KY',
        5: 'Toronto, OH',
        6: 'Paris, TX',
        7: 'Singapur, PR',
        8: 'China, TX',
        9: 'Chinatown, NY',
        10: 'Spain Park, AL'
    }

    options = "\n".join([f"[{key}] {value}" for key, value in location_choices.items()])
    location_input = simpledialog.askstring("Select Location", f"Choose Your Location:\n\n{options}")
    
    try:
        location_input = int(location_input)
        if location_input in location_choices:
            location_input_data = location_choices[location_input]
        else:
            raise ValueError
    except (ValueError, TypeError):
        location_input_data = ''  # Default to empty if input is invalid or canceled

    print(f"Selected location is: {location_input_data}")
    return location_input_data


def main():
    # Input designation and location
    designation_value = initial_profession_seter()
    location_value = initial_location_seter()

    # Initialize WebDriver
    main_driver = webdriver.Chrome()

    # Set the URL (replace with your target URL)
    URL = f'https://www.indeed.com/'
    main_driver.get(URL)

    # Wait for and interact with the Search button
    WebDriverWait(main_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[starts-with(text(), 'Search')]"))
    ).click()

    # Wait for the input fields to be present
    designation_input_element = WebDriverWait(main_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="text-input-what"]'))
    )
    designation_input_element.clear()
    designation_input_element.send_keys(designation_value)

    location_input_element = WebDriverWait(main_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="text-input-where"]'))
    )
    location_input_element.clear()
    location_input_element.send_keys(location_value)

    search_button_element = main_driver.find_element(By.XPATH, "//button[starts-with(text(), 'Search')]")
    search_button_element.click()

    # Wait for the search results to load
    main_element = WebDriverWait(main_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="mosaic-jobResults"]'))
    )

    # Define the upload folder and file path
    upload_folder = "upload"
    output_file_path = os.path.join(upload_folder, "job_cards.txt")

    # Ensure the upload folder exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Ensure the file exists by creating it if not already present
    if not os.path.exists(output_file_path):
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write("")  # Create an empty file

    # Find job cards
    professional_obj = WebDriverWait(main_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='mosaic-provider-jobcards']"))
    )
    professional_obj_li = professional_obj.find_elements(By.XPATH, ".//ul//li")  # Use relative XPath

    # Write job card details to the file
    with open(output_file_path, "w", encoding="utf-8") as file:
        for job in professional_obj_li:
            file.write(job.text + "\n")  # Write each job card's text into the file

    print(f"Job card details saved to {output_file_path}")

    time.sleep(5)
    main_driver.quit()


if __name__ == "__main__":
    main()
