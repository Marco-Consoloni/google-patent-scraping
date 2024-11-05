import os
import json
import argparse
from scraping_functions import setup_driver, get_title, get_abstract, get_CPC_classes, get_first_claim, download_img
import random

def scrape_documents_from_query(json_file_path, front_imgs_dir_output, json_dir_output, sample_size=5): 
    """
    Scrape patent documents based on citations from the specified JSON file.
    
    Parameters:
    - json_file_path (str): The path to the input JSON file containing patent data of a query patent.
    - front_imgs_dir_output (str): Directory where front images of document patents will be saved.
    - json_dir_output (str): Directory where patent data of the document patents  will be saved as a JSON file.
    - sample_size (int): number of documents to be scraped from the citation list of the query

    This function reads patent query data from a JSON file, extracts citation information.
    Then, for each cited patent (document patentens), it scrapes patent data and downloads the corresponding front image.
    """

    # Determine the CPC class of the corresponding query from the directory structure of the JSON file path
    CPC_class = os.path.dirname(json_file_path).split(os.path.sep)[-1]
    
    # Create the output directory for JSON files based on the CPC class
    json_dir_CPC = os.path.join(json_dir_output, CPC_class)
    os.makedirs(json_dir_CPC, exist_ok=True)
    front_imgs_dir_CPC = os.path.join(front_imgs_dir_output, CPC_class)
    os.makedirs(front_imgs_dir_CPC, exist_ok=True)

    # Initialize WebDriver
    driver = setup_driver()  
    
    # Open the json file for the patent query
    with open(json_file_path, 'r') as file:
        query_ID = os.path.splitext(os.path.basename(json_file_path))[0]
        query_data = json.load(file)
        citations_list = query_data.get('citations_by_examiner') # Retrieve the list of patent IDs cited by the examiner.
        print(f'\nScraping query: {query_ID} ...')

        # Check if citations list is not empty
        if len(citations_list) >= sample_size: # either 0 or sample_size
            random.seed(1999) 
            random.shuffle(citations_list) # shuflle the citations lists to iterate randomly over the citation list
            scraped_count = 0 # initialize counter for successfully scraped patents
            #citations_to_sample = min(len(citations_list), sample_size) # if the citation list has fewer elements than sample_size, it will sample the entire list
            #citations_list_rand = random.sample(citations_list, citations_to_sample) # get random elements from the citation list

            # Iterate over each patent ID in the citations list
            for patent_ID in citations_list:
                url = f"https://patents.google.com/patent/{patent_ID}/en?oq={patent_ID}" # Construct the Google Patents URL for the specific patent
                doc_ID = f'{query_ID}_{patent_ID}'
                json_filepath = os.path.join(json_dir_CPC, f'{doc_ID}.json') # Define the filename path for the output JSON file based on the patent ID

                # Ensure patent ID has not been scraped yet
                if os.path.exists(json_filepath):
                    print(f"{doc_ID} already scraped.")
                    scraped_count += 1
                    continue

                # Necessary when resuming scraping
                if scraped_count >= sample_size:
                    print(f"Successfully scraped {scraped_count} patents, stopping further scraping for this query.")
                    break
                
                # List of scraping functions with their arguments 
                scraping_functions = [
                    (get_abstract, driver, url),
                    (get_title, driver, url),
                    (get_CPC_classes, driver, url),
                    (get_first_claim, driver, url),
                    (download_img, driver, url, doc_ID, front_imgs_dir_CPC)
                ]

                results = []
                for func, *args in scraping_functions:
                    try:
                        result = func(*args)
                        assert result, f"Function: {func.__name__}() failed."
                        results.append(result)
                    except Exception as e:
                        # If any function fails, log the error and break the loop
                        print(f"Stopping execution due to failure in {func.__name__}().")
                        break 

                # If all functions succeed, assign results and proceed
                if len(results) == len(scraping_functions):
                    abstract, title, CPC_classes, fst_claim, front_img_path = results
                    document_patent_data = {
                        "type": "document",
                        "patent_ID": patent_ID,
                        "query_ID": query_ID,
                        "cls": CPC_class,
                        "title": title,
                        "abstract": abstract,
                        "CPC_class": CPC_classes,
                        "first_claim": fst_claim,
                        "front_img": front_img_path 
                    }
                    # Write the document patent data dictionary to a JSON file
                    with open(json_filepath, 'w') as json_file:
                        json.dump(document_patent_data, json_file, indent=2)
                        print(f"{doc_ID} successfully scraped.")
                    
                    # Increment the scraped count and check if target is reached
                    scraped_count += 1
                    if scraped_count == sample_size:
                        print(f"Successfully scraped {scraped_count} patents, stopping further scraping for this query.")
                        break
                else:
                    print(f"{doc_ID} from: {url} not succesfully scraped due to an earlier failure.")
            
            print(f"Scraping completed. Successfully scraped {scraped_count} patents.")  

        else:
            print(f'Scraping completed. Citations by examiner are less than {sample_size} for: {query_ID}')
            #print(f'Scraping completed. No citations found for: {query_ID}')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Scrape document patents associated to query patents and save JSON files.')

    parser.add_argument('--json_dir_input', type=str, default='/vast/marco/Data_Google_Patent/json/query',
                        help='Directory to read JSON files of the query patents.')
    parser.add_argument('--front_imgs_dir_output', type=str, default='/vast/marco/Data_Google_Patent/front_imgs/document',
                        help='Directory to save front images of the document patents.')
    parser.add_argument('--json_dir_output', type=str, default='/vast/marco/Data_Google_Patent/json/document',
                        help='Directory to save JSON files of the document patents.')
    parser.add_argument('--CPC_to_exclude', type=list, default=['H02K19'],
                        help="CPC file to exclude when resuming scraping. Example: ['A42B3', 'A62B18', 'F04D17', 'F16H1', 'F16L1', 'G02C5','H02K19']")
    args = parser.parse_args()  

# Iterate through each CPC directory within the input JSON directory
for CPC_dir in os.listdir(args.json_dir_input):
    CPC_dir_path = os.path.join(args.json_dir_input, CPC_dir)

    if CPC_dir in args.CPC_to_exclude:
        print(f'CPC: {CPC_dir} already scraped.')
        continue
    
    # Iterate through each JSON file in the current CPC directory.
    print(f'\nStarting scraping for CPC: {CPC_dir} ...')
    for json_file in os.listdir(CPC_dir_path):
        json_file_path = os.path.join(CPC_dir_path, json_file)
        scrape_documents_from_query(json_file_path, args.front_imgs_dir_output, args.json_dir_output)
    print(f'Completed scraping for CPC: {CPC_dir}')

    