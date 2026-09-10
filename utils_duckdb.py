import duckdb
    
####################
### BEG Config
####################

#datafile_json = "menu_items.json"
#table_name = "menu_items"

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

def get_conn():
    return duckdb.connect(database=':memory:')


def get_schema_from_json(datafile_json, table_name, conn=None):
    # to query against this connection, keep/create/return as appropriate, otherwise the in-memory context will be lost
    if(conn == None): conn = get_conn()

    # Connect the JSON file and treat it as a standard relational table
    conn.execute(f"CREATE VIEW raw AS SELECT row, metadata FROM read_json_auto('{datafile_json}')")
    # unnest() to flatten the *known* output from the pdf scrape
    conn.execute(f"CREATE VIEW {table_name} as select UNNEST(row) AS i, UNNEST(metadata) AS m from raw").fetchall()

    # Infer/create schema automatically
    #schema_info = conn.execute("DESCRIBE {table_name}").fetchall()
    #schema_info = conn.execute("DESCRIBE SELECT * FROM read_json_auto('data.json')").fetchall()
    #NOTE: customizing the presentation of the schema with the intention of making it more informative for the LLM
    schema_info = conn.execute(f"""
        SELECT table_name, column_name, data_type 
        FROM duckdb_columns() 
        WHERE table_name = '{table_name}'
    """).fetchall()
    # format the schema info for LLM usage, eg, double quotes around all DB obj names
    schema_string = "\n".join([f"Column: \"{row[0]}\".\"{row[1]}\", Type: {row[2]}" for row in schema_info])

    return schema_string, conn




