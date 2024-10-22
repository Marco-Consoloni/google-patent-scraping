import os
import json
import argparse
from scraping_functions import setup_driver, get_title, get_abstract, get_CPC_classes, get_first_claim, download_img
import random


def scrape_documents_from_query(json_file_path, front_imgs_dir_output, json_dir_output): 
    """
    Scrapes patent documents based on citations from the specified JSON file.
    
    Parameters:
    - json_file_path (str): The path to the input JSON file containing patent data of a query patent.
    - front_imgs_dir_output (str): Directory where front images of document patents will be saved.
    - json_dir_output (str): Directory where patent data of the document patents  will be saved as a JSON file.

    This function reads patent query data from a JSON file, extracts citation information.
    Then, for each cited patent (document patentens), it scrapes patent data and downloads the corresponding front image.
    """

    # Determine the CPC class of the corresponding query from the directory structure of the JSON file path
    CPC_class = os.path.dirname(json_file_path).split(os.path.sep)[-1]

    # Create the output directory for JSON files based on the CPC class
    json_dir_CPC = os.path.join(json_dir_output, CPC_class)
    os.makedirs(json_dir_CPC, exist_ok=True)

    # Create the output directory for front images based on the CPC class
    front_imgs_dir_CPC = os.path.join(front_imgs_dir_output, CPC_class)
    os.makedirs(front_imgs_dir_CPC, exist_ok=True)

    # Initialize WebDriver
    driver = setup_driver()  
    
    # Open the json file for the patent query
    with open(json_file_path, 'r') as file:
        query_patent_ID = os.path.splitext(os.path.basename(json_file_path))[0]
        query_patent_data = json.load(file)
        citations_list = query_patent_data.get('citations_by_examiner') # Retrieve the list of patent IDs cited by the examiner.
        print(f'\nStarting scraping for query: {query_patent_ID}')

        # Initialize a counter to keep track of the number of document patents successfully scraped
        retrieved_count = 0 

        # Check if citations list is not empty
        if len(citations_list) > 0:
            # Get random elements from the citation list
            sample_size = 5 # set a sample size
            random.seed(1999) # set the seed for reproducibility
            citations_to_sample = min(len(citations_list), sample_size) # If the citation list has fewer elements than sample_size, it will sample the entire list
            citations_list_rand = random.sample(citations_list, citations_to_sample) 

            # Iterate over each patent ID in the citations list
            for document_patent_ID in citations_list_rand:
                url = f"https://patents.google.com/patent/{document_patent_ID}/en?oq={document_patent_ID}" # Construct the Google Patents URL for the specific patent
                json_filepath = os.path.join(json_dir_CPC, f'{query_patent_ID}_{document_patent_ID}.json') # Define the filename path for the output JSON file based on the patent ID

                # Ensure patent ID has not been scraped yet
                if os.path.exists(json_filepath):
                    print(f"{document_patent_ID} already scraped.")
                    retrieved_count += 1 # Increment the count of successfully retrieved document patents
                    continue

                # List of scraping functions with their arguments 
                functions_with_args = [
                    (get_abstract, driver, url),
                    (get_title, driver, url),
                    (get_CPC_classes, driver, url),
                    (get_first_claim, driver, url),
                    (download_img, driver, url, f'{query_patent_ID}_{document_patent_ID}', front_imgs_dir_CPC)
                ]

                results = []
                for func_tuple in functions_with_args:
                    func = func_tuple[0]
                    args = func_tuple[1:]

                    try:
                        result = func(*args)
                        assert result, f"Function: {func.__name__}() failed."
                        results.append(result)

                    except Exception as e:
                        # If any function fails, log the error and break the loop
                        print(f"Stopping execution due to failure in {func.__name__}().")
                        break 

                # If all functions succeed, assign results and proceed
                if len(results) == len(functions_with_args):
                    
                    # Unpack results
                    abstract = results[0]
                    title = results[1]
                    CPC_classes = results[2]
                    fst_claim = results[3]
                    front_img_path = results[4]

                    # Create the patent data if all functions were successful
                    document_patent_data = {
                        "type": "document",
                        "query": json_file_path,
                        "patent_ID": document_patent_ID,
                        "class": CPC_class,
                        "title": title,
                        "abstract": abstract,
                        "CPC_class": CPC_classes,
                        "first_claim": fst_claim,
                        "front_img": front_img_path 
                    }

                    # Write the document patent data dictionary to a JSON file
                    with open(json_filepath, 'w') as json_file:
                        json.dump(document_patent_data, json_file, indent=2)
                        #print(f'{document_patent_ID} successfully scraped.')
                        
                    # Increment the count of successfully retrieved document patents
                    retrieved_count += 1
                                
                else:
                    print(f"{document_patent_ID} from: {url} not succesfully scraped due to an earlier failure.")
            
            # Print a summary of the results, showing how many patents were successfully scraped for the query patent
            print(f"\nScraping completed. N. of scraped document patents is: {retrieved_count}\t"
                    f"{retrieved_count}/{len(citations_list_rand)}\t"
                    f"{retrieved_count * 100 / len(citations_list_rand):.2f}%")
                     
        else:
            print(f'No citations by examiner found for: {query_patent_ID}')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Scrape document patents associated to query patents and save JSON files.')

    parser.add_argument('--json_dir_input', type=str, default='/vast/marco/Data_Google_Patent/json/query',
                        help='Directory to read JSON files of the query patents.')
    parser.add_argument('--front_imgs_dir_output', type=str, default='/vast/marco/Data_Google_Patent/front_imgs/document',
                        help='Directory to save front images of the document patents.')
    parser.add_argument('--json_dir_output', type=str, default='/vast/marco/Data_Google_Patent/json/document',
                        help='Directory to save JSON files of the document patents.')
    parser.add_argument('--CPC_to_exclude', type=list, default=['A62B18', 'F04D17', 'F16H1', 'F16L1', 'G02C5','H02K19'],
                        help="CPC file to exclude when resuming scraping. Example: ['A42B3', 'A62B18', 'F04D17', 'F16H1', 'F16L1', 'G02C5','H02K19']")
    args = parser.parse_args()  

# Iterate through each CPC directory within the input JSON directory
for CPC_dir in os.listdir(args.json_dir_input):
    CPC_dir_path = os.path.join(args.json_dir_input, CPC_dir)

    if CPC_dir in args.CPC_to_exclude:
        print(f'CPC: {CPC_dir} already scraped.')
        continue
    
    # Iterate through each JSON file in the current CPC directory.
    print(f'\nStarting scraping for CPC: {CPC_dir}')
    for json_file in os.listdir(CPC_dir_path):
        json_file_path = os.path.join(CPC_dir_path, json_file)
        scrape_documents_from_query(json_file_path, args.front_imgs_dir_output, args.json_dir_output)
    print(f'Completed scraping for CPC: {CPC_dir}')

    