import pyautogui
import subprocess
import time

import cv2




# def take_full_screenshot():
#     time.sleep(2)
#     screenshot = pyautogui.screenshot()
#     screenshot.save('full_screenshot.png')
#     print("Screenshot saved as 'full_screenshot.png'.")


# def find_button_in_image(screenshot_path, button_template_path):
#     # Load the full screenshot and the button template
#     screenshot = cv2.imread(screenshot_path)
#     button_template = cv2.imread(button_template_path)

#     # Convert both images to grayscale for template matching
#     screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
#     button_gray = cv2.cvtColor(button_template, cv2.COLOR_BGR2GRAY)

#     # Perform template matching to find the button
#     result = cv2.matchTemplate(screenshot_gray, button_gray, cv2.TM_CCOEFF_NORMED)

#     # Get the best match location (highest correlation value)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

#     # Get the size of the template (button) image
#     h, w = button_gray.shape

#     # Get the top-left corner of the matched area and calculate the bottom-right corner
#     top_left = max_loc
#     bottom_right = (top_left[0] + w, top_left[1] + h)

#     # Highlight the matched region in the screenshot (for visual debugging)
#     cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
#     cv2.imwrite('result_with_button_highlighted.png', screenshot)

#     # Print and return the coordinates of the matched button
#     print(f"Button found at: x={top_left[0]}, y={top_left[1]}, width={w}, height={h}")
#     return top_left[0], top_left[1], w, h

# def take_screenshot_and_find_button():
#     # Take a new screenshot
#     screenshot_path = 'full_screenshot.png'
#     pyautogui.screenshot(screenshot_path)

#     # Path to the pre-cropped template image of the button
#     button_template_path = 'enable_button.png'  # This should be your pre-cropped image

#     # Find the button in the new screenshot
#     x, y, width, height = find_button_in_image(screenshot_path, button_template_path)

#     # Use pyautogui to move to the button and click it
#     pyautogui.moveTo(x + width / 2, y + height / 2, duration=1)
#     pyautogui.click()

# # Run the function to take a screenshot, find the button, and click it



def search_and_open_hideme():
    pyautogui.hotkey('win', 's')
    time.sleep(1)
    
    pyautogui.write('hide.me VPN', interval=0.1)
    time.sleep(2)
    
    pyautogui.press('enter')
    time.sleep(5)

    # take_screenshot_and_find_button()

    

    # # Retry mechanism to search for the "Enable VPN" button
    # for attempt in range(5):
    #     # Locate the "Enable VPN" button on the screen without confidence
    #     button_location = pyautogui.locateOnScreen('enable_button.png')
        
    #     if button_location:
    #         button_x, button_y = pyautogui.center(button_location)
    #         # Move to the button and click it
    #         pyautogui.moveTo(button_x, button_y, duration=1)
    #         pyautogui.click()
    #         print("Enable VPN button clicked.")
    #         break
    #     else:
    #         print(f"Attempt {attempt + 1}: Enable button not found, retrying...")
    #         time.sleep(2)
    # else:
    #     print("Failed to find the Enable VPN button after 5 attempts.")

# Run the function
search_and_open_hideme()

# def search_and_open_hideme():
#     pyautogui.hotkey('win', 's')
#     time.sleep(1)

#     pyautogui.write('hide.me VPN', interval=0.1)
#     # Delay to switch to the app

#     time.sleep(2)
    
#     pyautogui.press('enter')
#     time.sleep(3)

#     # Locate the "Enable VPN" button on the screen
#     button_location = pyautogui.locateOnScreen('enable_button.png')

#     if button_location:
#         button_x, button_y = pyautogui.center(button_location)
#         # Move and click the button
#         pyautogui.moveTo(button_x, button_y, duration=1)
#         pyautogui.click()
#     else:
#         print("Enable button not found on the screen.")


# # Run the function
# search_and_open_hideme()
