import json
import utils_chroma as utils
import utils_pdf as up

####################
### BEG Config
####################

PDF_FILE_NAME = "ChilisMenu.pdf"

DATA_IN_PFX = "./data/in/"
DATA_OUT_PFX = "./data/out/"
OUTPUT_COLLECTION = "pdf_data"

####################
### END Config
####################

PDF_FILE_PATH = DATA_IN_PFX + PDF_FILE_NAME
OUTPUT_DB = DATA_OUT_PFX + "chroma_db"
OUTPUT_JSON = DATA_OUT_PFX + PDF_FILE_NAME + ".json"

# --- Execution ---
if __name__ == "__main__":

    up.convert_pdf_to_imgs(PDF_FILE_PATH, "./annotate/"+PDF_FILE_NAME)

    extracted_data = up.find_text_from_pdf(PDF_FILE_PATH)

    if extracted_data:
        utils.store_in_chromadb(extracted_data, OUTPUT_DB, collection_name=OUTPUT_COLLECTION)

        with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, indent=4)

    else:
        print("No tabular data found in the PDF.")

    exit()
