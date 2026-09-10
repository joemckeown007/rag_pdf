import json
import utils_pdf as up
    
####################
### BEG Config
####################

PDF_FILE_NAME = "Chilis Nutrition Menu Generic.pdf" 

DATA_IN_PFX = "./data/in/"
DATA_OUT_PFX = "./data/out/"
    
####################
### END Config
####################

pdf_file_path = DATA_IN_PFX + PDF_FILE_NAME
output_json = DATA_OUT_PFX + PDF_FILE_NAME + ".json"

# --- Execution ---
if __name__ == "__main__":

    extracted_data = up.find_tables_from_pdf(pdf_file_path)

    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(extracted_data, file, indent=4)

    exit()
