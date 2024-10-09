from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scraping_functions import get_patent_PN_from_url, get_citations, get_front_img_url, download_img
import json

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # (Optional) Disable sandboxing for better performance
chrome_options.add_argument("--disable-dev-shm-usage")  # (Optional) Overcome limited resource problems

# Create a WebDriver instance with the Service object and options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Define urls to webpages
#url = 'https://patents.google.com/patent/US20240008586A1/en?oq=US20240008586A1'
urls = ['https://patents.google.com/patent/US20240008586A1/en?oq=US20240008586A1',
        'https://patents.google.com/patent/CN203952623U/en?oq=CN203952623U',
        'https://patents.google.com/patent/US20130283639A1/en?oq=US20130283639A1']

# Store citations data into a jsonl file
filename = "patent_citations.jsonl"
with open(filename, 'w', encoding='utf-8') as file:

    for url in urls:
        patent_ID = get_patent_PN_from_url(url)
        citations_by_examiner, citations = get_citations(driver, url)

        # Create a dictionary to store the citation data
        patent_data = {
            "patent_ID": patent_ID,
            "citations_by_examiner": citations_by_examiner,
            "citations": citations,
            "all_citations": citations_by_examiner + citations
        }

        # Convert the dictionary to a JSON string and write it as a new line
        file.write(json.dumps(patent_data) + '\n')

# Close the browser to free up resources 
driver.quit()


