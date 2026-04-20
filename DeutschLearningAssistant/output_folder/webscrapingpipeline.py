import time
import random
import os
import requests
import base64
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def setup_driver():
    """Configures the Selenium WebDriver."""
    options = Options()
    # options.add_argument("--headless") # Uncomment to run without a window
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

def scrape_pinterest(search_query, num_scrolls=3):
    """Scrapes Pinterest and returns a list of high-res image URLs."""
    driver = setup_driver()
    all_urls = set()
    
    try:
        url = f"https://www.pinterest.com/search/pins/?q={search_query}"
        driver.get(url)
        time.sleep(5)

        for i in range(num_scrolls):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for img in soup.find_all("img"):
                src = img.get("src")
                if src and "i.pinimg.com" in src:
                    # Upgrade to high-res
                    high_res = src.replace("236x", "736x") 
                    all_urls.append(high_res) if isinstance(all_urls, list) else all_urls.add(high_res)
            
            driver.execute_script("window.scrollBy(0, 2000);")
            print(f"Scroll {i+1}: Collected {len(all_urls)} URLs")
            time.sleep(random.uniform(2, 4))

        return list(all_urls)
    finally:
        driver.quit()

def download_images(url_list, folder_name="downloads"):
    """Downloads and saves the images to a local directory."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print(f"Starting download to '{folder_name}' folder...")
    
    for i, url in enumerate(url_list):
        try:
            # Handle standard URLs
            if url.startswith("http"):
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    img = Image.open(BytesIO(resp.content))
                    # Save as JPEG
                    img.save(f"{folder_name}/image_{i+1}.jpg")
                    print(f"Saved image {i+1}")
            
        except Exception as e:
            print(f"Failed to save image {i+1}: {e}")

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    query = "apple pie"
    # 1. Scrape
    found_pins = scrape_pinterest(query, num_scrolls=2)
    
    # 2. Download (Replacing the Jupyter display logic)
    download_images(found_pins, folder_name=query.replace(" ", "_"))
    
    print("\nProcess Complete!")