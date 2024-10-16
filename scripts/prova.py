from scraping_functions import setup_driver, get_CPC_classes, get_abstract
import re

url = "https://patents.google.com/patent/US2969547A/en?oq=US+4443891+A"
url = "https://patents.google.com/patent/US9777980B2/en?q=(gun)&oq=gun"
url = "https://patents.google.com/patent/US11807335B2/en?q=(bike)&oq=bike"
#driver = setup_driver()
#abstract = get_abstract(driver, url)
#print(abstract)
#scraped = get_CPC_classes(driver, url)
#print(f'Scraped: {scraped}')

citations = []
print(citations is not None)

#match = re.search(r'^[A-Z][\d]{2}[A-Z]\d*\/\d*\s', "A42B3/0023ciao")
#print(f'Test: {match}')