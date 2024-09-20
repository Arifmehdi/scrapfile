import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

# Scraping function
def scrape_aliexpress(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Modify these selectors based on AliExpress structure
        title = soup.find('h1', {'class': 'product-title-text'}).get_text(strip=True)
        price = soup.find('span', {'class': 'product-price-value'}).get_text(strip=True)
        description = soup.find('div', {'class': 'product-description'}).get_text(strip=True)

        # Combine data into a formatted string to show in the GUI
        data = f"Title: {title}\nPrice: {price}\nDescription: {description}\n"
        return data

    except Exception as e:
        return f"Error: {str(e)}"

# GUI setup
def scrape_and_show():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Input Error", "Please enter a valid URL")
        return

    result = scrape_aliexpress(url)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

# Create main window
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
