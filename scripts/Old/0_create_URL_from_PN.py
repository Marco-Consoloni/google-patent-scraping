import os

txt_folder = r'C:\Users\acer\Desktop\Google_Patent_Scraping\query_patent_from_USPTO'
txt_files = os.listdir(txt_folder)
output_folder = r'C:\Users\acer\Desktop\Google_Patent_Scraping\query_patent_URL'

for txt_filename in txt_files: 
    output_file = os.path.join(output_folder, txt_filename) # Create a output file
    
    # Open the output file in write mode
    with open(output_file, 'w') as out_file:
        txt_path = os.path.join(txt_folder, txt_filename)
        print(f"\nReading file: {txt_filename}")
        
        # Open the file and read line by line
        with open(txt_path, 'r') as file:
            for line in file:
                patent_ID = line.replace(" ", "").strip()
                url = f"https://patents.google.com/patent/{patent_ID}/en?oq={patent_ID}"
                
                # Write the generated URL to the output file
                out_file.write(url + "\n")

