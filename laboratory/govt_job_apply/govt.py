
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
    # base_url = "http://ecs.teletalk.com.bd/"
    base_url = "http://dncc.teletalk.com.bd/"
    return base_url


def main():
    main_driver = initialize_webdriver()
    targated_url = custom_url()

    URL = targated_url
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    logging.info(URL)
    main_driver.get(URL)


    time.sleep(5)
    # Wait until the form with id="recruitment" is clickable
    form = WebDriverWait(main_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//form[@id="recruitment"]'))
    )

    submit_button = WebDriverWait(form, 10).until(
        EC.element_to_be_clickable((By.XPATH, './/a'))
    )
    submit_button.click()
    logging.info("Clicked the Applied Link")


    time.sleep(2)  # Adjust if needed
    main_driver.switch_to.window(main_driver.window_handles[-1])  # Switch to the new tab

    # Wait until the form is present in the new tab
    apply_form = WebDriverWait(main_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//form[@id="recruitment"]'))
    )

    # Find the PDF link inside the form
    pdf_link = apply_form.find_element(By.XPATH, './/a[contains(@href, ".pdf")]')
    pdf_url = pdf_link.get_attribute("href")

    if pdf_url and pdf_url.endswith(".pdf"):
        logging.info(f"Found PDF link: {pdf_url}")
        
        # Download the PDF
        response = requests.get(pdf_url, headers=HEADER, stream=True)
        if response.status_code == 200:
            pdf_filename = "downloaded_file.pdf"
            with open(pdf_filename, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    pdf_file.write(chunk)
            logging.info(f"PDF downloaded successfully: {pdf_filename}")
        else:
            logging.warning("Failed to download PDF.")
    else:
        logging.warning("No PDF link found.")

    time.sleep(5)
    try:
        application_form_link = WebDriverWait(main_driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, './/a[contains(text(), "Application Form (Click here to Apply Online)")]'))
        )
        application_form_link.click()
        logging.info("Clicked the 'Application Form (Click here to Apply Online)' link")
    except Exception as e:
        logging.error(f"Failed to find or click the link: {e}")
    


        premium_apply_form = WebDriverWait(main_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//form[@id="postForm"]'))
        )

        premium_radio_button = premium_apply_form.find_elements(By.XPATH,'//input[@onclick="ebableSubmit()"]')

        premium_radio_button.click()
        print("Checked the prepost  radio button.")



    postForm = WebDriverWait(main_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//form[@id="postForm"]'))
    )

    radio_datas = postForm.find_elements(By.XPATH,'//input[@onclick="ebableSubmit()"]')

    if radio_datas:
        # Display each option with an index number for the user to select
        for index, radio_data in enumerate(radio_datas):
            # Get the value and associated text (label) of each radio button
            value = radio_data.get_attribute("value")
            label_text = radio_data.find_element(By.XPATH, './following-sibling::span').text  # Assuming the label text is in the span after the input
            print(f"{index + 1}. {label_text} (Value: {value})")
        
        # Prompt the user to select a choice by entering a number
        choice = int(input("Enter the number of your choice: ")) - 1  # Subtract 1 to match the index

        # Verify the choice is within range and click the chosen radio button
        if 0 <= choice < len(radio_datas):
            selected_radio = radio_datas[choice]
            selected_radio.click()  # Click the selected radio button
            print(f"You selected option: {choice + 1}")
            
            next_button = WebDriverWait(postForm, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@id="submit"]'))
            )
            next_button.click()
            print("Clicked the Next button for apply form.")
        else:
            print("Invalid choice. Please run the code again and choose a valid option.")

        premium_apply_form = WebDriverWait(main_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//form[@id="permiumForm"]'))
        )

        no_radio_button = premium_apply_form.find_element(By.XPATH, '//input[@id="nid_02"]')
        no_radio_button.click()
        print("Checked the 'No' radio button.")

        # Find the "Next" button and ensure it's clickable
        premium_next_button = WebDriverWait(premium_apply_form, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@name="submitPremium"]'))
        )

        # Click the "Next" button
        premium_next_button.click()
        print("Clicked the premium 'Next' button.")
    time.sleep(5)

    name_data = 'Md. Arif Mehedi'
    bn_name_data = 'মোঃ আরিফ মেহেদী'
    father_name_data = 'Md. Nurul Islam'
    bn_father_name_data = 'মোঃ নুরুল ইসলাম'
    mother_name_data = 'Aklima Begum'
    bn_mother_name_data = 'আকলিমা বেগম'
    dob_data = '03-01-1994'
    gender_data = 'Male'
    boolean_true = '1' 
    boolean_false = '0' 
    nid_data = 1930790140
    breg_data = 19943090549052730
    maritual_status_data = 'Married'
    spouse_data = 'Mousumi Akter'
    mobile_data = '01925923276'
    email_data = 'mehediarif.du@gmail.com'
    quota_data = 'Md. Nurul Islam , M-16521, 22-05-2003 '
    present_careof_data = 'MD. ZAKIR HOSSAIN MOLLA'
    present_village_data = '304/1, Dhanmondi 15 no(old new 8/a)'
    present_post_data = 'JIGATOLA'
    present_postcode_data = '1209'

    parmanent_careof_data = 'Md. Aziz'
    parmanent_village_data = 'MODHUPUR VOTTO'
    parmanent_post_data = 'Gopalpur'
    parmanent_postcode_data = '1990'


    application_form = WebDriverWait(main_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//form[@id="applicationForm"]'))
    )
    name_info = application_form.find_element(By.XPATH,'//input[@id="name"]') 
    name_info.clear()
    name_info.send_keys(name_data)

    bn_name_info = application_form.find_element(By.XPATH,'//input[@id="name_bn"]') 
    bn_name_info.clear()
    bn_name_info.send_keys(bn_name_data)

    father_name_info = application_form.find_element(By.XPATH,'//input[@id="father"]') 
    father_name_info.clear()
    father_name_info.send_keys(father_name_data)

    father_bn_name_info = application_form.find_element(By.XPATH,'//input[@id="father_bn"]') 
    father_bn_name_info.clear()
    father_bn_name_info.send_keys(bn_father_name_data)

    mother_name_info = application_form.find_element(By.XPATH,'//input[@id="mother"]') 
    mother_name_info.clear()
    mother_name_info.send_keys(mother_name_data)

    mother_bn_name_info = application_form.find_element(By.XPATH,'//input[@id="mother_bn"]') 
    mother_bn_name_info.clear()
    mother_bn_name_info.send_keys(bn_mother_name_data)

    dob_info = application_form.find_element(By.XPATH,'//input[@id="dob"]') 
    dob_info.clear()
    dob_info.send_keys(dob_data)

    gender_info = application_form.find_element(By.XPATH,'//select[@id="gender"]') 
    gender_select = Select(gender_info)
    gender_select.select_by_value(gender_data)


    religion_info = application_form.find_element(By.XPATH,'//select[@id="religion"]') 
    religion_select = Select(religion_info)
    religion_select.select_by_value(boolean_true)


    nid_info = application_form.find_element(By.XPATH,'//select[@id="nid"]') 
    nid_select = Select(nid_info)
    nid_select.select_by_value(boolean_true)

    WebDriverWait(application_form, 10).until(EC.visibility_of_element_located((By.ID, "nid_no")))

    # Locate the National ID input field and set its value
    nid_input = application_form.find_element(By.XPATH, '//input[@id="nid_no"]')
    nid_input.send_keys(nid_data)


    breg_info = application_form.find_element(By.XPATH,'//select[@id="breg"]') 
    breg_select = Select(breg_info)
    breg_select.select_by_value(boolean_true)

    WebDriverWait(application_form, 10).until(EC.visibility_of_element_located((By.ID, "breg_no")))

    # Locate the National ID input field and set its value
    nid_input = application_form.find_element(By.XPATH, '//input[@id="breg_no"]')
    nid_input.send_keys(breg_data)

    passport_info = application_form.find_element(By.XPATH,'//select[@id="passport"]') 
    passport_select = Select(passport_info)
    passport_select.select_by_value(boolean_false)

    maritual_status_info = application_form.find_element(By.XPATH,'//select[@id="marital_status"]') 
    maritual_status_select = Select(maritual_status_info)
    maritual_status_select.select_by_value(maritual_status_data)

    WebDriverWait(application_form, 10).until(EC.visibility_of_element_located((By.ID, "spouse_name")))

    # Locate the National ID input field and set its value
    maritual_input = application_form.find_element(By.XPATH, '//input[@id="spouse_name"]')
    maritual_input.send_keys(spouse_data)

    mobile_input = application_form.find_element(By.XPATH, '//input[@id="mobile"]')
    mobile_input.send_keys(mobile_data)

    confirm_mobile_input = application_form.find_element(By.XPATH, '//input[@id="confirm_mobile"]')
    confirm_mobile_input.send_keys(mobile_data)

    email_input = application_form.find_element(By.XPATH, '//input[@id="email"]')
    email_input.send_keys(email_data)

    quota_status_info = application_form.find_element(By.XPATH,'//select[@id="quota"]') 
    quota_status_select = Select(quota_status_info)
    quota_status_select.select_by_value(boolean_true)

    WebDriverWait(application_form, 10).until(EC.visibility_of_element_located((By.ID, "quota_details")))

    # Locate the National ID input field and set its value
    quota_input = application_form.find_element(By.XPATH, '//input[@id="quota_details"]')
    quota_input.send_keys(quota_data)

    present_care_info_input = application_form.find_element(By.XPATH, '//input[@id="present_careof"]')
    present_care_info_input.send_keys(present_careof_data)

    present_village_info_input = application_form.find_element(By.XPATH, '//textarea[@id="present_village"]')
    present_village_info_input.send_keys(present_village_data)

    present_post_info_input = application_form.find_element(By.XPATH, '//input[@id="present_post"]')
    present_post_info_input.send_keys(present_post_data)

    present_postcode_input = application_form.find_element(By.XPATH, '//input[@id="present_postcode"]')
    present_postcode_input.send_keys(present_postcode_data)




    parmanent_care_info_input = application_form.find_element(By.XPATH, '//input[@id="permanent_careof"]')
    parmanent_care_info_input.send_keys(parmanent_careof_data)

    parmanent_village_info_input = application_form.find_element(By.XPATH, '//textarea[@id="permanent_village"]')
    parmanent_village_info_input.send_keys(parmanent_village_data)

    parmanent_post_info_input = application_form.find_element(By.XPATH, '//input[@id="permanent_post"]')
    parmanent_post_info_input.send_keys(parmanent_post_data)

    parmanent_postcode_input = application_form.find_element(By.XPATH, '//input[@id="permanent_postcode"]')
    parmanent_postcode_input.send_keys(parmanent_postcode_data)

# quota
# present_careof
# present_village
# present_district
# present_post
# present_postcode

    print("[0] Quit")
    print("[1] Stay")
    user_mode = int(input('Please choose what you want: '))

    if user_mode == 0: 
        main_driver.quit()
    # main_driver.close()
    # main_driver.switch_to.window(main_driver.window_handles[0])  # Switch back to the first tab



if __name__ == "__main__":
    main()