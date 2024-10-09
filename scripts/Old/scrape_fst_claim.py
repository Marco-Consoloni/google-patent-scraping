from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scraping_functions import get_patent_PN_from_url, get_first_claim
import json

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # (Optional) Disable sandboxing for better performance
chrome_options.add_argument("--disable-dev-shm-usage")  # (Optional) Overcome limited resource problems

# Create a WebDriver instance with the Service object and options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Define urls to webpages
url = 'https://patents.google.com/patent/US20240008586A1/en?oq=US20240008586A1'

fst_claim = get_first_claim(driver, url)
    
driver.quit()