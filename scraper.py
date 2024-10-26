import os
import re
import time
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright
# 03335489016

import csv

cities_csv_file = "uscities.csv"
cities_to_scrape = 1
pages_to_scroll = 2
with_html = False
is_headless = False
professions = [
    "Plumbers",
    "Electricians",
    "Landscapers",
    "Flooring Contractors",
    "Roofers",
    "HVAC Technicians (Heating, Ventilation, and Air Conditioning)",
    "Painters (Interior and Exterior)",
    "Window Installers and Repair Specialists",
    "Carpenters",
    "Pest Control Services",
    "Masonry Contractors (Brick and Stone Work)",
    "Pool Maintenance and Repair",
    "Garage Door Installers and Repair Technicians",
    "Handyman Services",
    "Appliance Repair Technicians",
    "Gutter Installation and Cleaning Services",
    "Drywall Installers and Repair Technicians",
    "Security System Installers",
    "Fence Builders and Repair Services",
    "Solar Panel Installers",
    "General Contractors",
    "Home Inspectors",
    "Waterproofing Specialists",
    "Chimney Sweeps and Repair Technicians",
    "Pressure Washing Services",
    "Interior Designers",
    "Tree Removal and Trimming Services",
    "Basement Finishing Contractors",
    "Window Cleaners",
    "Insulation Contractors",
    "Tile and Grout Cleaning Specialists",
    "Cabinet Makers and Installers",
    "Deck Builders and Repair Services",
    "Hardwood Floor Refinishers",
    "Siding Contractors",
    "Door Installation and Repair Services",
    "Home Theater Installation Specialists",
    "Moving and Packing Services",
    "Smart Home Automation Installers",
]

city_names = []

with open(cities_csv_file, "r") as file:
    reader = csv.reader(file)
    for row in reader:
        city_names.append(row[0])



# Function to clean HTML
def clean_html(html_code):
    """
    Cleans the HTML code to make it suitable for saving.
    
    - Removes newlines, tabs, and carriage returns.
    - Collapses multiple spaces into one.
    - Removes excess whitespace between HTML tags.
    
    :param html_code: The HTML code string to be cleaned.
    :return: A cleaned HTML code string.
    """
    cleaned_html = re.sub(r'[\n\r\t]', ' ', html_code)
    cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)
    cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
    cleaned_html = cleaned_html.strip()
    return cleaned_html


def run_base(page, profession, city, pages_to_scroll, get_html=False):
    """Shared base logic for both run functions."""
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


def run_with_map_card(playwright, profession, cities, pages_to_scroll):
    """Includes the 'map_card' field and outputs to a text file."""
    businesses = []
    browser = playwright.chromium.launch(headless=is_headless)
    page = browser.new_page()
    
    for city in cities:
        print(f"City {city}")
        new_businesses = run_base(page, profession, city, pages_to_scroll, get_html=True)
        businesses = businesses + new_businesses

    # Write to text file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = "output"  # Define the output folder path
    os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist
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


def run_without_map_card(playwright, profession, cities, pages_to_scroll):
    """Excludes the 'map_card' field and outputs to a CSV file."""
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
    
    all_fieldnames = list(all_fieldnames)  # Convert to list for DictWriter

    # Write to CSV
    if businesses:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = "output"  # Define the output folder path
        os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist
        output_filename = os.path.join(output_folder, f"{profession}_{timestamp}.csv")

        with open(output_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)
            writer.writeheader()  # Write column names as the first row
            writer.writerows(businesses)  # Write data rows
    
    browser.close()

with sync_playwright() as playwright:
    cities=city_names[1:cities_to_scrape + 1]
    
    for profession in professions:
        start_cpu_time = time.time()
        
        if with_html:
            run_with_map_card(playwright, profession, cities, pages_to_scroll)
        else:
            run_without_map_card(playwright, profession, cities, pages_to_scroll)
        
        end_cpu_time = time.time()
        execution_time = end_cpu_time - start_cpu_time

        print(f"Execution time: {execution_time:.6f} seconds")
