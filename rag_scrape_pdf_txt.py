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

    #up.convert_pdf_to_imgs(PDF_FILE_PATH, "./annotate/"+PDF_FILE_NAME)

    metadata_boxes = [
  {
    "id": "cc1583f4-f7cb-476d-a4fb-7ed9ca81a3ad",
    "text": "menu_category: appetizers",
    "x0": 18.99916577737274,
    "y0": 165.87696013046988,
    "x1": 583.6205452262581,
    "y1": 762.9501119474086
  },
  {
    "id": "60a66ddd-fded-4ea5-baec-12ba4a40541a",
    "text": "category: store name address phone",
    "x0": 401.9507171121289,
    "y0": 66.70911007939999,
    "x1": 603.2325962611607,
    "y1": 152.44798508675572
  },
  {
    "id": "c2f22fb2-453f-44f5-ae77-7438f97e7000",
    "text": "spicy",
    "x0": 3.5159806002048923,
    "y0": 580.1093690453506,
    "x1": 582.5882991868622,
    "y1": 707.1682209469154
  }
]
    
    
    text_parsers = [
        r"(?i)\$(?P<dollars>\d+)\.(?P<cents>\d{2})"
        , r"(?i)\$(?P<price>\d+\.\d{2})"
        , r"(?i)(?P<menu_item_name>.*) - .*\$\d+\.\d{2}.*"
        , r"(?i).*(?P<contains_dairy>(cream|sour cream|cheese|milk|queso|quesa))"
        , r"(?i).*(?P<contains_nuts>(peanut|almond|hazelnut))"
  ]
    
    extracted_data = up.find_text_from_pdf(PDF_FILE_PATH, metadata_boxes, text_parsers)

    if extracted_data:
        #utils.store_in_chromadb(extracted_data, OUTPUT_DB, collection_name=OUTPUT_COLLECTION)

        with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, indent=4)

    else:
        print("No tabular data found in the PDF.")

    exit()
