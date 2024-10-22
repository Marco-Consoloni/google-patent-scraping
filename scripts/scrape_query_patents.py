import os
import json
import argparse
from scraping_functions import setup_driver, get_citations, get_title, get_abstract, get_CPC_classes, get_first_claim, download_img

def scrape_queries_from_CPC(CPC_file_path, front_imgs_dir_output, json_dir_output):
    """
    Scrape patent data for a given CPC class from Google Patents and save a JSON file for each patent of the CPC class.

    Parameters:
    - CPC_file_path (str): The file path containing the list of patent IDs belonging to a specific CPC class.
    - front_imgs_dir_output (str): Directory where front images of patents will be saved.
    - json_dir_output (str): Directory where the scraped patent data will be saved as a JSON file.

    This function reads patent IDs from the specified CPC class file, scrapes patent data such as
    citations, first claims, and front images from Google Patents for each query patent, and stores
    the results in a dictionary. The dictionary is then saved to a JSON file corresponding to the patent ID of the query patent.
    """

    # Initialize WebDriver
    driver = setup_driver()  

    try:
        with open(CPC_file_path, 'r') as file:
            CPC_class = os.path.splitext(os.path.basename(CPC_file_path))[0]
            
            # Create the json directory for the CPC class
            json_dir_CPC = os.path.join(json_dir_output, CPC_class)
            os.makedirs(json_dir_CPC, exist_ok=True)

            # Create the front img directory for the CPC class
            front_imgs_dir_CPC = os.path.join(front_imgs_dir_output, CPC_class)
            os.makedirs(front_imgs_dir_CPC, exist_ok=True)

            # Iterate the patents of the CPC class (one patent ID per line)
            for line in file:
                patent_ID = line.replace(" ", "").strip()  # Clean the patent ID by removing spaces and line breaks
                url = f"https://patents.google.com/patent/{patent_ID}/en?oq={patent_ID}" # Construct the Google Patents URL for the specific patent
                json_filepath = os.path.join(json_dir_CPC, f"{patent_ID}.json") # Create  json file path where to store patent data

                # Ensure patent ID has not been scraped yet
                if os.path.exists(json_filepath):
                    print(f"{patent_ID} already scraped.")
                    continue

                # List of scraping functions with their arguments 
                functions_with_args = [
                    (get_abstract, driver, url),
                    (get_citations, driver, url),
                    (get_title, driver, url),
                    (get_CPC_classes, driver, url),
                    (get_first_claim, driver, url),
                    (download_img, driver, url, patent_ID, front_imgs_dir_CPC)
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
                    citations_by_examiner, citations = results[1] 
                    title = results[2]
                    CPC_classes = results[3]
                    fst_claim = results[4]
                    front_img_path = results[5]

                    # Create and save the patent data if all functions were successful
                    patent_data = {
                        "type": "query",
                        "patent_ID": patent_ID,
                        "class": CPC_class,
                        "title": title,
                        "abstract": abstract,
                        "CPC_class": CPC_classes,
                        "citations_by_examiner": citations_by_examiner,
                        "citations": citations,
                        "all_citations": citations_by_examiner + citations,
                        "first_claim": fst_claim,
                        "front_img": front_img_path 
                    }
                    
                    # Write the patent data dictionary to a JSON file
                    with open(json_filepath, 'w') as json_file:
                        json.dump(patent_data, json_file, indent=2)
                        print(f'{patent_ID} successfully scraped.')

                else:
                    print(f"{patent_ID} from: {url} not succesfully scraped due to an earlier failure.")

    # Ensure driver is closed after processing is complete
    finally:
        driver.quit()  


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Scrape Google Patents and save patent data for query patents as JSON.')

    parser.add_argument('--CPC_class_dir', type=str, default='/home/fantoni/marco/google-patent-scraping/CPC_class',
                        help='Directory containing CPC files, each storing patent IDs of query patents for a specific CPC class.')
    parser.add_argument('--front_imgs_dir_output', type=str, default='/vast/marco/Data_Google_Patent/front_imgs/query',
                        help='Directory to save front images of query patents.')
    parser.add_argument('--json_dir_output', type=str, default='/vast/marco/Data_Google_Patent/json/query',
                        help='Directory to save JSON files of query patents.')
    parser.add_argument('--CPC_to_exclude', type=list, default=['A62B18.txt', 'F04D17.txt', 'F16H1.txt', 'F16L1.txt', 'G02C5.txt','H02K19.txt'], 
                        help="list of CPC file to exclude when resuming scraping. Example: ['A42B3.txt', 'A62B18.txt', 'F04D17.txt', 'F16H1.txt', 'F16L1.txt', 'G02C5.txt','H02K19.txt']")

    args = parser.parse_args() 

    # Get the list of all CPC files in the directory provided by the user.
    # Then iterate over the CPC files (each file corresponds to a specific CPC class).
    CPC_files = os.listdir(args.CPC_class_dir)
    for CPC_file in CPC_files:
        CPC_file_path = os.path.join(args.CPC_class_dir, CPC_file)

        if CPC_file in args.CPC_to_exclude:
            print(f'CPC: {CPC_file} already scraped.')
            continue

        print(f'\nStarting scraping for CPC: {CPC_file}')
        scrape_queries_from_CPC(CPC_file_path, args.front_imgs_dir_output, args.json_dir_output)
        print(f'Completed scraping for CPC: {CPC_file}')

            




