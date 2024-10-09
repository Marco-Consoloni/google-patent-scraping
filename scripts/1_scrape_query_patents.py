import os
import json
import argparse
from scraping_functions import setup_driver, get_citations, get_first_claim, download_img


def scrape_queries_from_CPC(CPC_file_path, front_imgs_dir, json_dir):
    """
    Scrape patent data for a given CPC class from Google Patents and save a JSON file for each patent of the CPC class.

    Parameters:
    - CPC_file_path (str): The file path containing the list of patent IDs belonging to a specific CPC class.
    - front_imgs_dir (str): Directory where front images of patents will be saved.
    - json_dir (str): Directory where the scraped patent data will be saved as a JSON file.

    This function reads patent IDs from the specified CPC class file, scrapes data such as
    citations, first claims, and front images from Google Patents for each patent, and stores
    the results in a dictionary. The dictionary is then saved to a JSON file corresponding to the patent ID.
    """

    # Initialize WebDriver
    driver = setup_driver()  

    try:
        with open(CPC_file_path, 'r') as file:
            CPC_class = os.path.splitext(os.path.basename(CPC_file_path))[0]
            
            # Create the json directory for the CPC class
            json_dir_CPC = os.path.join(json_dir, CPC_class)
            os.makedirs(json_dir_CPC, exist_ok=True)

            # Create the front img directory for the CPC class
            front_imgs_dir_CPC = os.path.join(front_imgs_dir, CPC_class)
            os.makedirs(front_imgs_dir_CPC, exist_ok=True)

            # Iterate the patents of the CPC class (one patent ID per line)
            for line in file:
                patent_ID = line.replace(" ", "").strip()  # Clean the patent ID by removing spaces and line breaks
                # Construct the Google Patents URL for the specific patent
                url = f"https://patents.google.com/patent/{patent_ID}/en?oq={patent_ID}" 

                try:
                    # Scrape patent data 
                    citations_by_examiner, citations = get_citations(driver, url)
                    fst_claim = get_first_claim(driver, url)
                    front_img_path = download_img(driver, url, filename=patent_ID, save_dir=front_imgs_dir_CPC)

                    # Ensure that citations by examiner, first claim, and front image are successfully retrieved
                    if len(citations_by_examiner) != 0 and fst_claim and front_img_path:

                        # Create a dictionary to hold all the scraped data for this patent  
                        patent_data = {
                            "type": "query",
                            "CPC_class": CPC_class,
                            "citations_by_examiner": citations_by_examiner,
                            "citations": citations,
                            "all_citations": citations_by_examiner + citations,
                            "first_claim": fst_claim,
                            "front_img": front_img_path 
                        }
                        
                        json_filename = patent_ID + '.json'
                        json_filepath = os.path.join(json_dir_CPC, json_filename)

                        # Write the patent data dictionary to a JSON file
                        with open(json_filepath, 'w') as json_file:
                            json.dump(patent_data, json_file, indent=2)
                            print(f'{patent_ID} successfully scraped.')

                # Handle any exceptions that occur during scraping for a particular patent
                except Exception as e:
                    print(f"Error processing patent {patent_ID} from {url}: {e}")

    # Ensure driver is closed after processing is complete
    finally:
        driver.quit()  


if __name__ == "__main__":

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape Google Patents and save patent data for queries as JSON.')
    parser.add_argument('--CPC_class_dir', type=str, default=r'C:\Users\acer\Desktop\Google_Patent_Scraping\CPC_class',
                        help='Directory containing CPC files, each storing patent IDs for a specific CPC class.')
    parser.add_argument('--front_imgs_dir', type=str, default=r'C:\Users\acer\Desktop\Google_Patent_Scraping\front_imgs\query',
                        help='Directory to save front images.')
    parser.add_argument('--json_dir', type=str, default=r'C:\Users\acer\Desktop\Google_Patent_Scraping\json\query',
                        help='Directory to save JSON files.')

    args = parser.parse_args()  # Parse command-line arguments.

    # Get the list of all CPC files in the directory provided by the user.
    # Then iterate over the CPC files (each file corresponds to a specific CPC class).
    CPC_files = os.listdir(args.CPC_class_dir)
    for CPC_file in CPC_files:
        CPC_file_path = os.path.join(args.CPC_class_dir, CPC_file)
        print(f'Starting the scraping process for CPC: {CPC_file} -------------------')
        scrape_queries_from_CPC(CPC_file_path, args.front_imgs_dir, args.json_dir)
        print(f'Completed scraping process for CPC: {CPC_file} ----------------------')




