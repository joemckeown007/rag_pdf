import json
import utils_chroma as utils
import utils_pdf as up

####################
### BEG Config
####################

PDF_FILE_NAME = "ChilisMenu.pdf"

DATA_IN_PFX = "./data/in/"
DATA_OUT_PFX = "./data/out/"
OUTPUT_COLLECTION = "pdf_data" # make sure this is the same as when querying

####################
### END Config
####################

PDF_FILE_PATH = DATA_IN_PFX + PDF_FILE_NAME
OUTPUT_DB = DATA_OUT_PFX + "chroma_db"
OUTPUT_JSON_EXT = ".json"
OUTPUT_JSON = DATA_OUT_PFX + PDF_FILE_NAME + OUTPUT_JSON_EXT

# --- Execution ---
if __name__ == "__main__":

    #up.convert_pdf_to_imgs(PDF_FILE_PATH, "./annotate/"+PDF_FILE_NAME)

    # each page's box data is pasted in from the annotate.html app
    metadata_boxes ={
      "pg1": [
  {
    "id": "cc1583f4-f7cb-476d-a4fb-7ed9ca81a3ad",
    "text": "menu_category: appetizers | starters",
    "x0": 18.99916577737274,
    "y0": 165.87696013046988,
    "x1": 583.6205452262581,
    "y1": 762.9501119474086
  },
  {
    "id": "60a66ddd-fded-4ea5-baec-12ba4a40541a",
    "text": "category: store name | address | phone",
    "x0": 401.9507171121289,
    "y0": 66.70911007939999,
    "x1": 603.2325962611607,
    "y1": 152.44798508675572
  },
  {
    "id": "c2f22fb2-453f-44f5-ae77-7438f97e7000",
    "text": "is_spicy: spicy",
    "x0": 3.515980600204898,
    "y0": 580.1093690453506,
    "x1": 582.5882991868622,
    "y1": 713.7854988589179
  }
]
      , "pg2": [
  {
    "id": "57ead144-b3e0-4c8e-8104-cddf40dd7735",
    "text": "menu_category: appetizers | starters",
    "x0": 9.709267610963952,
    "y0": 17.125178551913333,
    "x1": 582.5882991868622,
    "y1": 76.00609913720633
  },
  {
    "id": "cce48f5a-ebe7-4f11-91e7-d1e93033777b",
    "text": "menu_category: SOUPS | SALADS | SIDES",
    "x0": 15.898682469429048,
    "y0": 70.89060360209515,
    "x1": 585.6849680035368,
    "y1": 766.0491328629394
  }
]
      , "pg6": [
  {
    "id": "df59c343-2f02-4e94-95fe-9a3f96b523ba",
    "text": "beverages: soda | fountain drinks | tea | coffee | lemonade | water | shake",
    "x0": 16.93476898816167,
    "y0": 708.2011816826578,
    "x1": 572.2661853004696,
    "y1": 773.2801354297436
  }
]
      , "pg7": [
  {
    "id": "ed23d01b-cf6c-427c-9c16-ed04dad612af",
    "text": "beverages: soda | fountain drinks | tea | coffee | lemonade | water | shake",
    "x0": 24.160270365359388,
    "y0": 16.092164716898456,
    "x1": 571.2339739118304,
    "y1": 183.43793416399524
  },
  {
    "id": "2d5c97d4-37c7-421b-a922-1963b2c5b22e",
    "text": "beverages: margarita | rita",
    "x0": 9.709267610963952,
    "y0": 187.5699331538065,
    "x1": 580.5238764095837,
    "y1": 487.1395044750941
  },
  {
    "id": "2ebd523b-c7c3-47bb-bb4e-8b068c11a2fa",
    "text": "beverages: wine | cabernet | merlot | pinot | zinfadel",
    "x0": 10.741482248111646,
    "y0": 497.4694932803533,
    "x1": 588.781636820211,
    "y1": 768.1151236885761
  }
]
      , "pg8": [
  {
    "id": "37add60b-e1cb-4ba1-9fe6-85b9b0bbc33c",
    "text": "beverages: beer",
    "x0": 13.83812615955473,
    "y0": 15.059181224324954,
    "x1": 583.6205452262581,
    "y1": 126.62302174287683
  }
]
    }

    metadata_parsers = [
        r"(?i)\$(?P<dollars>\d+)\.(?P<cents>\d{2})"
        , r"(?i)\$(?P<price>\d+\.\d{2})"
        , r"(?i)(?P<menu_item>.*) - .*\$\d+\.\d{2}.*"
        , r"(?i).*(?P<contains_dairy>(cream|sour cream|cheese|milk|queso|quesa))"
        , r"(?i).*(?P<contains_nuts>(peanut|almond|hazelnut))"
        , r"(?i).*(?P<is_spicy>(spicy))"
  ]
    
    extracted_data = up.find_text_from_pdf(PDF_FILE_PATH, metadata_boxes, metadata_parsers)

    if extracted_data:
        #utils.store_in_chromadb(extracted_data, OUTPUT_DB, collection_name=OUTPUT_COLLECTION)

        with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, indent=4)

    else:
        print("No tabular data found in the PDF.")

    exit()
