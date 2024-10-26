import os
import re
import time
import csv
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from playwright.sync_api import sync_playwright
import sys

# Function to clean HTML
def clean_html(html_code):
    cleaned_html = re.sub(r'[\n\r\t]', ' ', html_code)
    cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)
    cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
    cleaned_html = cleaned_html.strip()
    return cleaned_html

# Function to redirect print statements to the GUI Text widget
class PrintLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.config(state=NORMAL)

    def write(self, message):
        self.text_widget.insert(END, message)
        self.text_widget.see(END)  # Scroll to the end

    def flush(self):
        pass

def run_base(page, profession, city, pages_to_scroll, get_html=False):
    cleaned_city_name = city.replace(" ", "+")
    cleaned_profession_name = profession.replace(" ", "+")
    query = f"{cleaned_profession_name}+in+{cleaned_city_name}"
    local_service_search_url = f"https://www.google.com/maps/search/{query}"
    print(local_service_search_url)
    page.goto(local_service_search_url)
    time.sleep(2)

    base_xpath = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]"
    html_card_element = '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div'

    result_window = page.query_selector(f"xpath={base_xpath}")
    for _ in range(pages_to_scroll):
        result_window.evaluate("el => el.scrollBy(0, 1000)")
        time.sleep(2)

    businesses = []
    for i in range(3, 300, 2):
        try:
            result_xpath = f"{base_xpath}/div[{i}]/div"
            element = page.query_selector(f"xpath={result_xpath}")
            if not element:
                continue

            business_info = {
                "profession": profession,
                "city": city,
            }

            business_name_div = element.query_selector(".fontHeadlineSmall")
            if business_name_div:
                business_info["business_name"] = business_name_div.inner_text()

            rating_div = page.query_selector(f"xpath={result_xpath}/div[2]/div[4]/div[1]/div/div/div[2]/div[3]/div/span[2]/span/span[1]")
            total_ratings_div = page.query_selector(f"xpath={result_xpath}/div[2]/div[4]/div[1]/div/div/div[2]/div[3]/div/span[2]/span/span[2]")
            address_div = page.query_selector(f"xpath={result_xpath}/div[2]/div[4]/div[1]/div/div/div[2]/div[4]/div[1]")
            open_time_div = page.query_selector(f"xpath={result_xpath}/div[1]/div[1]/div[29]/div/div[2]/div[4]/div[1]/div/div/div[2]/div[4]/div[2]/span[1]/span")
            phone_number_div = page.query_selector(f"xpath={result_xpath}/div[2]/div[4]/div[1]/div/div/div[2]/div[4]/div[2]/span[2]/span[2]")
            website_div = page.query_selector(f"xpath={result_xpath}/div[2]/div[4]/div[2]/div[1]/a")

            if rating_div:
                business_info["rating"] = rating_div.inner_text()
            if total_ratings_div:
                business_info["total_ratings"] = total_ratings_div.inner_text()[1:-1]
            if address_div:
                address_str = address_div.inner_text()
                address_str = address_str[address_str.find("Â· ") + 3:]
                business_info["address"] = address_str
            if open_time_div:
                business_info["open_time"] = open_time_div.inner_text()
            if phone_number_div:
                business_info["phone_number"] = phone_number_div.inner_text()
            if website_div:
                business_info["website"] = website_div.get_attribute("href")

            if get_html:
                element.click()
                time.sleep(2)
                html_card_div = page.query_selector(f"xpath={html_card_element}")
                business_info["html"] = clean_html(html_card_div.inner_html())

            businesses.append(business_info)

        except Exception as e:
            print(f"Error: {e}")
            pass

    return businesses

def run_with_map_card(playwright, profession, cities, pages_to_scroll, is_headless):
    businesses = []
    browser = playwright.chromium.launch(headless=is_headless)
    page = browser.new_page()

    for city in cities:
        print(f"City {city}")
        new_businesses = run_base(page, profession, city, pages_to_scroll, get_html=True)
        businesses = businesses + new_businesses

    # Write to text file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_filename = os.path.join(output_folder, f"{profession}_with_html_card_{timestamp}.txt")

    with open(output_filename, mode="w", encoding="utf-8") as txtfile:
        for business in businesses:
            for key, value in business.items():
                try:
                    txtfile.write(f"{key}: {value}\n")
                except Exception as e:
                    print(f"Error writing {key}: {e}")
            txtfile.write("\n" + "-"*40 + "\n")

    browser.close()

def run_without_map_card(playwright, profession, cities, pages_to_scroll, is_headless):
    businesses = []
    browser = playwright.chromium.launch(headless=is_headless)
    page = browser.new_page()

    for city in cities:
        print(f"Profession: {profession} City: {city}")
        new_businesses = run_base(page, profession, city, pages_to_scroll)
        businesses = businesses + new_businesses

    all_fieldnames = set()
    for business in businesses:
        all_fieldnames.update(business.keys())

    all_fieldnames = list(all_fieldnames)

    # Write to CSV
    if businesses:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, f"{profession}_{timestamp}.csv")

        with open(output_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)
            writer.writeheader()
            writer.writerows(businesses)

    browser.close()


# GUI Functions
def run_scraper():
    cities_csv_file = file_entry.get()
    cities_to_scrape = int(cities_entry.get())
    pages_to_scroll = int(pages_entry.get())
    is_headless = bool(headless_var.get())
    is_headless = not is_headless
    with_html = bool(html_var.get())

    professions_list = professions_entry.get("1.0", END).strip().splitlines()

    city_names = []
    with open(cities_csv_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            city_names.append(row[0])

    cities = city_names[1:cities_to_scrape]

    with sync_playwright() as playwright:
        for profession in professions_list:
            if with_html:
                run_with_map_card(playwright, profession, cities, pages_to_scroll, is_headless)
            else:
                run_without_map_card(playwright, profession, cities, pages_to_scroll, is_headless)

    messagebox.showinfo("Execution Complete", "Scraping has completed successfully!")


def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    file_entry.delete(0, END)
    file_entry.insert(0, filename)


# GUI Setup
root = Tk()
root.title("Google Businesses Scraping Tool")
root.geometry("400x700")

# Redirect print statements to a Text widget
output_text = Text(root, height=10, width=60, wrap="word")
output_text.pack(pady=10)
sys.stdout = PrintLogger(output_text)  # Redirect print statements to Text widget

# Labels and Entries
Label(root, text="Cities CSV File").pack(pady=5)
file_entry = Entry(root, width=50)
file_entry.pack(pady=5)
Button(root, text="Browse", command=browse_file).pack(pady=5)

Label(root, text="Number of Cities to Scrape").pack(pady=5)
cities_entry = Entry(root, width=10)
cities_entry.pack(pady=5)

Label(root, text="Pages to Scroll").pack(pady=5)
pages_entry = Entry(root, width=10)
pages_entry.pack(pady=5)

Label(root, text="Professions (one per line)").pack(pady=5)
professions_entry = Text(root, height=5, width=50)
professions_entry.pack(pady=5)

# Checkbuttons for options
headless_var = IntVar()
Checkbutton(root, text="Show browser while scraping", variable=headless_var).pack(pady=5)

html_var = IntVar()
Checkbutton(root, text="Include HTML in Output", variable=html_var).pack(pady=5)

# Run button
Button(root, text="Run Scraper", command=run_scraper).pack(pady=20)

root.mainloop()
