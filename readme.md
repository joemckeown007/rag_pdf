# Toy RAG / ETL demo:
## PDF -> DATA -> DB -> AI -> SQL -> RESULTS

### what is RAG & ETL, etc.; define stuff

### A bare-bones demonstration of extracting data from a multi-page PDF, processing and storing it, and then using an AI chat model to make natural language queries against it.

## Ingestion of PDF as text then processing it with 2 separate methods to extract metadata
### #1 Annotate PDF pages with box areas on each page to associate with metadata
- The annotate.html web page app is a tool to generate those boxes for each page in the PDF
- Screenshot and example data format of the annotation web page app
![Annotation app screenshot and example data format](imgs/annotate_ex01.png)
- Regions/boxes on the page define metadata for each page in the PDF:
```
{
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
}
```
- Text lines that are within a box will have that box's metadata applied to it
- The JSON data from the annotate.html app is then used in the PDF processing

### #2 Parse each line on the a page to extract data points for metadata usage
- Parsing / extract metadata of semantic value to aid in retrieval
```
# Python code snippet defining RegEx patterns for data parsing/extraction, each of them being applied to every line of data...

r"(?i)\$(?P<dollars>\d+)\.(?P<cents>\d{2})"
, r"(?i)\$(?P<price>\d+\.\d{2})"
, r"(?i)(?P<menu_item>.*) - .*\$\d+\.\d{2}.*"
, r"(?i).*(?P<contains_dairy>(cream|sour cream|cheese|milk|queso|quesa))"

```
### Both metadata extraction processes yield a combined data obj for each line in the data, for example:
```
# Python JSON code snippet for a data object for a line in the data...
    {
        "id": "pg_1_ln_39",
        "row": "BONELESS SHANGHAI WINGS - $8.29",
        "metadata": {
            "menu_category": [
                "appetizers",
                "starters"
            ],
            "is_spicy": [
                "spicy"
            ],
            "dollars": 8.0,
            "cents": 29.0,
            "price": 8.29,
            "menu item": "boneless shanghai wings",
            "page": 1,
            "line": 39,
            "source": "./data/in/chilismenu.pdf"
        }
    },

```
- Embedding / vectorize that data into persistant chromadb along with the metadata will allow for more usable and accurate search results

## PDF TABLE -> DATA TABLE -> JSON -> AI -> SQL -> RESULTS
- Natural text to sql will then query that json data to answer the question:
    - "Show the menu items name, calories and protein with more than 70 grams of protein, sorted by protein in descending order."
    - Generated SQL:
    ```
    SELECT "menu_items"."menu_item", TRY_CAST("menu_items"."Prot (g)" AS FLOAT) AS Protein, "menu_items"."Cals" FROM menu_items WHERE TRY_CAST("menu_items"."Prot (g)" AS FLOAT) > 70 ORDER BY Protein DESC
    ```

    - Query Results:
    ```
    ('Classic Nachos - Beef - Large', 109.0, '1590')
    ('Classic Nachos - Chicken - Large', 99.0, '1420')
    ('Classic Ribeye', 86.0, '1280')
    ('Memphis Dry Rub Ribs - Full Rack', 84.0, '1690')
    ('Original Ribs - Full Rack', 82.0, '1580')
    ('Bacon Ranch Beef Quesadilla', 80.0, '1800')
    ('Chipotle Chicken', 79.0, '1320')
    ('California Grilled Chicken', 77.0, '1450')
    ('Texas Cheese Fries - Full Order', 75.0, '1720')
    ('Bacon Ranch Chicken Quesadilla', 74.0, '1690')
    ('Classic Nachos - Beef - Regular', 73.0, '1090')
    ('Bacon Avocado Chicken Sandwich', 73.0, '1580')
    ('10 oz Classic Sirloin', 73.0, '1000')
    ('Cajun Pasta w/ Grilled Chicken', 71.0, '1270')
    ```

## Libraries
- Python 3.14, pdfplumber, ollama, chromadb, duckdb, json, regular expressions
- Ollama for running models, choose your own

## Misc
- try with postgreSQL?
- improve annotate app to save / reload state




