import ollama
import utils_duckdb as ud
    
####################
### BEG Config
####################

chat_model_value = "qwen2.5-coder:3b" # llama3.2 | gemma4:e2b-it-qat | qwen2.5-coder:3b

DATA_IN_PFX = "./data/in/"
DATA_OUT_PFX = "./data/out/"

JSON_FILE_NAME = "Chilis Nutrition Menu Generic.pdf.json" 

TABLE_NAME = "menu_items"

# Natural language question
user_question = "Show the top 3 menu items name and calories, sorted by calories in descending order."
user_question = "What is the average cals of all menu_items."
user_question = "Which menu items have cheese in their name?"
user_question = "Which menu item on the third page has the second most carbs?"
user_question = "Show the menu items name, calories and protein with more than 70 grams of protein, sorted by protein in descending order."
user_question = "For each menu item, show the name and the ratio of fat calories to total calories, sorted by the ratio in descending order."

####################
### END Config
####################

datafile_json = DATA_IN_PFX + JSON_FILE_NAME

schema_string, conn = ud.get_schema_from_json(datafile_json, TABLE_NAME)

system_prompt = (
    "## You are a DuckDB SQL expert. Given the schema of a JSON file below, write a raw SQL query to answer the question.\n"
    "## The schema of the data JSON file will have a hierarchical structure that will need to be considered in the output SQL.\n"
    "## Ensure to cast values appropriately for accurate results, with special attention to numeric types.\n"
    "## Column headers always use double quotes for any column names.\n"
    "## Avoid using table aliases.\n"
    "## Use fully qualified column names in the format \"table_name\".\"column_name\" to avoid ambiguity.\n"
    "## Use DuckDB's JSON dot-notation for nested fields (e.g., \"column_name\".\"sub_column_name\").\n"
    "## Do not wrap the response in markdown code blocks. Output ONLY the raw SQL string.\n"
    "## If null values will affect the results, exclude them with appropriate filtering in the SQL query.\n"
    "## ALWAYS use the pattern `TRY_CAST(\"column_name\".\"sub_column_name\" AS FLOAT) IS NOT NULL` to check for NULL.\n"
    "## Do not use the CAST() function.\n"
    "## Do not use the LIKE keyword, always use ILIKE for case insensitivity.\n"
    "## Do not use the BIGINT type, always use INT.\n"
    "## Put the null tests before any attempts to use a non-noll value.\n"
    "## Note: For nested JSON attributes, use DuckDB dot notation:\n"
    "- Use for accessing fields inside STRUCT data types.\n"
    "- Always wrap keys in double quotes (e.g., \"table_name\".\"column_name\").\n"
    "- For deeply nested structs, just add more dots (e.g., event_details.coordinates.x).\n"
)

# Build a Context-Aware Prompt
user_prompt = f"""
## Table name: {TABLE_NAME}

## Schema:

{schema_string}

Question: {user_question}
"""
print(user_prompt)
print("Thinking...")

response = ollama.chat(
    model=chat_model_value, # llama3.2 or gemma4:e2b-it-qat or qwen2.5-coder:3b
    options={"temperature": 0.0}, # 0 should give most deterministic responses
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)

print(f"🤖 Generated SQL:\n{response['message']['content']}\n")

# Execute the generated SQL against the JSON file via DuckDB
try:
    sql = response['message']['content']
    result = conn.execute(sql).fetchall()
    print("📊 Query Results:")
    #print(result)
    for row in result:
        print(row)

except Exception as e:
    print(f"❌ Execution Error: {e}")

finally:
    conn.close()

