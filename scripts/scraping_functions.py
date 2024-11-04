
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import requests

# To use Firefox driver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# To use Google Chorme driver
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():

    """Set up and return a headless Firefox WebDriver."""
    # Initialize FirefoxOptions
    firefox_options = Options()
    firefox_path = "/usr/bin/firefox"  # Set the path to the Firefox binary
    firefox_options.binary_location = firefox_path  # Set Firefox as the binary
    firefox_options.add_argument("--headless")  # Run Firefox in headless mode
    firefox_options.add_argument("--log-level=0")  # Suppress all logs (equivalent logging level for Firefox)
    firefox_options.add_argument("--disable-web-security")  # Optional: might help with web security issues
    firefox_options.add_argument("--no-sandbox")  # Not supported in Firefox, will be ignored
    firefox_options.add_argument("--disable-dev-shm-usage")  # Not needed for Firefox
    service = Service(executable_path="/usr/bin/geckodriver")  # Path to the GeckoDriver executable
    driver = webdriver.Firefox(service=service, options=firefox_options)

    """Set up and return a headless Chrome WebDriver."""
    # Intitialize Chrome options
    #chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    #chrome_options.add_argument("--log-level=0")  # Suppress All logs
    #chrome_options.add_argument("--disable-web-security")  # This might help with shadow DOM
    #chrome_options.add_argument("--no-sandbox")  # (Optional) Disable sandboxing for better performance
    #chrome_options.add_argument("--disable-dev-shm-usage")  # (Optional) Overcome limited resource problems
    #chrome_options.add_argument("--disable-features=site-per-process")  # This too
    
    # Create a WebDriver instance with the Service object and options
    #service=Service(ChromeDriverManager().install())
    #driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver



def get_patent_PN_from_citation_node(node_text, url):
    ''' 
    This function is used inside the get_citations() function.
    Extracts patent Publication Numbers (PN) from the text of the HTML element of citations and divide them 
    into two lists: those added by the examiner (indicated by an asterisk *) and 
    those without the asterisk. The asterisk is removed before appending to the list.
    '''
    try:
        citations_by_examiner = []
        citations = []
        # Split the text into rows using newline characters as delimiters
        rows = re.split(r'\n', node_text) 
        for row in rows:
            # Use a regular expression to search for a pattern that matches patent IDs in each row
            match = re.search(r'^[A-Z0-9]+\s\*?', row)
            if match:
                patent_PN = match.group().rstrip(' ')
                # Categorize based on whether the publication number ends with an asterisk (*)
                if patent_PN.endswith('*'):
                    citations_by_examiner.append(patent_PN.rstrip(' *'))
                else:
                    citations.append(patent_PN)

        return citations_by_examiner, citations
    except Exception as e:
        #print(f"Error processing HTML node for citations for: {url} Messag: {e}")
        return None



def get_citations(driver, url):
    '''
    This function navigates to a given URL using a Selenium WebDriver, locates an HTML element containing 
    citation information using XPath, extracts the text, and then parses it to return the patent IDs of the 
    citations. 
    '''
    # Navigate to the given URL
    driver.get(url)  
    # Define the Xpath to point the HTML node where patent citations are listed.
    xpath_citations_title ='/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[3]/h3[1]'
    xpath_citations = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[3]/div[1]'
    try:
        citations_title_node = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_citations_title)))
        # Ensure the section title for ""
        if re.search(r'^Patent Citations', citations_title_node.text): 
            citations_node = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_citations)))
            citations = get_patent_PN_from_citation_node(citations_node.text, url)
            return citations
    except Exception as e:
        #print(f"Error scraping citations from: {url} Message: {e}")
        return None



def get_title(driver, url):
    '''
    This function navigates to a given URL using a Selenium WebDriver, locates an HTML element containing 
    the title text using XPath. If successful, the text of the title is extracted and returned.
    '''
    # Navigate to the given URL
    driver.get(url)  
    # Define the Xpath to point the HTML node where title text is contained.
    xpath_title = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div[1]/div/h1'
    try:
        title_node = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_title)))
        title_text = title_node.text
        return title_text.strip() if title_text else None
    except Exception as e:
        #print(f"Error scraping title from: {url} Message: {e}")
        return None



def get_abstract(driver, url):
    '''
    This function navigates to a given URL using a Selenium WebDriver, locates an HTML element containing 
    the abstract text using XPath. If successful, the abstract is extracted and returned.
    '''
    # Navigate to the given URL
    driver.get(url)  
    # Define the Xpath to point the HTML node where title abstract is contained.
    xpath_abstract = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[1]/patent-text/div/section/abstract/div'
    try:
        abstract_node = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_abstract)))
        abstract_text = abstract_node.text
        return abstract_text.strip() if abstract_text else None
    except Exception as e:
        #print(f"Error scraping abstract from: {url} Message: {e}")
        return None



def get_first_claim(driver, url):
    '''
    This function navigates to a given URL using a Selenium WebDriver, locates an HTML element containing 
    the fisrt claim text using XPath. If successful, the text of the claim is extracted and returned.
    '''
    # Navigate to the given URL
    driver.get(url)  
    # Define the Xpath to point the HTML node where first calim text is contained.
    xpath_fst_claim = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[2]/div[2]/section/patent-text/div/section/div/div[1]/div'
    try:
        fst_claim_node = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_fst_claim)))
        fst_claim_text = fst_claim_node.text
        return fst_claim_text.strip() if fst_claim_text else None
    except Exception as e:
        #print(f"Error scraping first claim from: {url} Message: {e}")
        return None



def get_CPC_classes_from_HTML_node(node_text, url):
    ''' 
    This function is used inside the get_CPC_classes() function.
    Extracts patent CPC classes from the text of the HTML element of classificaiton viewr.
    '''
    try:
        CPC_classes = []
        # Split the text into rows using newline characters as delimiters
        rows = re.split(r'\n', node_text) 
        for row in rows:
            # Use a regular expression to search for a pattern that matches the CPC class in each row
            match = re.search(r'^[A-Z][\d]{2}[A-Z]\d*\/\d*\s?', row)
            if match:
                CPC_class = match.group().rstrip(' ')
                CPC_classes.append(CPC_class)
        return CPC_classes
    except Exception as e:
        #print(f"Error processing HTML element for CPC classes for: {url} Message: {e}")
        return None



def get_CPC_classes(driver, url):
    '''
    This function navigates to a given URL and clicks on a thumbnail to open a full classification viewer.
    It then locates the expanded classification viewer using a specified XPath, extracts the text,
    and then parses it to return the CPC classes. 
    '''
    # Navigate to the given URL
    driver.get(url)
    
    # Define the Xpath to find the thumbnail of the classification viewer.
    thumbnail_xpath  = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/div[1]'
    # Define the Xpath to point the HTML node where CPC classes are contained
    xpath_CPC_classes = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]'
    
    try:
        # Try to click the thumbnail
        try:
            thumbnail = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, thumbnail_xpath)))
            thumbnail.click() # # Click the thumbnail to expand the classification viewer
        except Exception as e:
            #print(f"Could not click CPC thumbnail for: {url}")
            # Continue execution even if click fails
            pass 

        # try to Get CPC classes regardless of whether the click succeeded, because some patents may not have the classification viewer.
        CPC_node = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_CPC_classes)))
        CPC_classes = get_CPC_classes_from_HTML_node(CPC_node.text, url)
        #print(f"Succesfully retrieved CPC class for: {url}")
        return CPC_classes
    
    except Exception as e:
        #print(f"Error scraping CPC classes from: {url} Message: {e}")
        return None
        

def get_front_img_url(driver, url):
    '''
    This function navigates to a given URL and clicks on a thumbnail to open a full image viewer.
    It then locates the full image using a specified XPath, extracts the src attribute (image URL), and returns it. 
    '''
    # Navigate to the given URL
    driver.get(url) 
    # Define the Xpath to the thumbnail of the full image viewer.
    thumbnail_xpath  = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[2]/image-carousel/div/img[1]'
    # Define the Xpath to point the HTML node of the full image viewer where the front image url is loacated.
    xpath_front_img = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div[2]/div[2]/image-viewer/div/div[2]/div[1]/img'
    try:
        # Try to click the thumbnail if it exists
        thumbnail = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, thumbnail_xpath)))
        thumbnail.click() # # Click to open full image viewer
        front_img_node = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_front_img)))
        front_img_url = front_img_node.get_attribute('src')
        if front_img_url:
            #print(f"Successfully found image URL: {front_img_url}")
            return front_img_url
        else:
            print(f"Image URL not found for: {url}")
            return None
    except Exception as e:
        #print(f"Error getting front img URL from: {url} Message: {e}")
        return None



def download_img(driver, url, filename, save_dir):
    '''
    This function downloads and saves the front image of a patent using its URL.
    It first retrieves the image URL via get_front_img_url().
    Then creates a directory (if it doesn't exist), and saves the image with the specified patent_ID as the filename in .png format.
    '''
    try:
        front_img_url = get_front_img_url(driver, url)
        if front_img_url:
            os.makedirs(save_dir, exist_ok=True)
            filename = f'{filename}.png'
            filepath = os.path.join(save_dir, filename)
            
            # Download the image
            response = requests.get(front_img_url, stream=True)
            response.raise_for_status() 
            
            # Save the image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            #print(f"Successfully downloaded image to: {filepath}")
            return filepath
        
    except Exception as e:
        #print(f"Error downloading image from: {url} Message: {e}")
        return None





    
