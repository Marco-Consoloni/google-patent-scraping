import os
import argparse
import json


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Parsing filenames of document patents get succesfully scraped patents for each query and save JSON for each CPC class.') 

    parser.add_argument('--json_dir_input', type=str, default='/vast/marco/Data_Google_Patent/json/document/',
                        help='Directory to read JSON files for document patents.')
    parser.add_argument('--output_dir', type=str, default='/vast/marco/Data_Google_Patent/ground_truth',
                        help='Directory to save JSON files witth gorund truth.')
    
    args = parser.parse_args()  # Parse command-line arguments.

    # Iterate through each CPC directory within the input JSON directory
    for CPC_class in os.listdir(args.json_dir_input):
        CPC_class_path = os.path.join(args.json_dir_input, CPC_class)
        
        # Initialize and empty dictionary to store the ground truth
        query_doc_truth = {}

        # Iterate over the doument patents in a CPC class
        for doc in os.listdir(CPC_class_path):
            doc_id = doc.replace('.json', '')
            query_id = f"{doc_id.split('_')[0]}_{doc_id.split('_')[1]}"
            # Check if the query ID is already a key in the dictionary
            if query_id in query_doc_truth:
                query_doc_truth[query_id].append(doc_id)
            else:
                query_doc_truth[query_id] = [doc_id]

        # Define the output path for this CPC class's JSON file
        output_file = os.path.join(args.output_dir, f"{CPC_class}.json")
        
        # Write the query_doc_truth to a JSON file for this CPC class
        with open(output_file, 'w') as f:
            json.dump(query_doc_truth, f, indent=4)

        print(f"Saved {CPC_class}.json")



            