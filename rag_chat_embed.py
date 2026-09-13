import ollama
import utils_chroma as uc

####################
### BEG Config
####################

chat_model_value = "qwen2.5-coder:3b" # "gemma4:e2b-it-qat" # "llama3.2" # 
num_ctx = 32768
model_temperature = 0.6 # 0 should give most deterministic responses


DATA_IN_PFX = "./data/in/"
DATA_OUT_PFX = "./data/out/"

QUERY_DB_PATH = DATA_OUT_PFX + "chroma_db"
QUERY_COLLECTION = "pdf_data"

USER_QUESTION = "What is the most expensive steak?"
USER_QUESTION = "How much does 'WINGS OVER BUFFALO' cost?" 
USER_QUESTION = "What are the options for the Create Your Own Combo?" 
USER_QUESTION = "Is the fried cheese spicy?" 
USER_QUESTION = "List all the menu items that have a price $5 or less."
USER_QUESTION = "Which menu items have cheese in their names?"
USER_QUESTION = "List all the CHARDONNAYs."
USER_QUESTION = "How many menu items are there total? List them with prices." 
USER_QUESTION = "List all the menu items that are spicy along with their price." 

WHERE_FILTER = {"is_spicy":{"$contains": "spicy"}} # None # {"price": {"$lte": 4.0}} # {"beverages":{"$contains": "wine"}} # 

####################
### END Config
####################


def answer_question_from_db(question, db_path, collection_name, where_filter=None):
    context = uc.get_query_from_chromadb(question, db_path=db_path, collection_name=collection_name, where_filter=where_filter)
    
    if not context.strip():
        print("No relevant context found in the database.")
        return
    
    # 3. Construct the prompt for the Chat Model
    system_prompt = (
        "You are an AI assistant answering questions based strictly on the provided table data context."
        "Avoid duplicate results."
        "If the answer cannot be found in the context, say that you do not know."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    print(user_prompt)
    # Generate response using Ollama chat (using llama3 as an example)
    print("\nThinking...")
    response = ollama.chat(
        model=chat_model_value,
        options={'num_ctx': num_ctx, "temperature":model_temperature}, 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    #print(f"\n[Retrieved Context Used]:\n{context}\n")
    #if (response['message']['thinking']) : print(f"[AI Thinking]:\n{response['message']['thinking']}")
    print(f"[AI Response]:\n{response['message']['content']}")


# --- Execution ---
if __name__ == "__main__":

    print(f"User Question: {USER_QUESTION}")
    answer_question_from_db(USER_QUESTION, db_path=QUERY_DB_PATH, collection_name=QUERY_COLLECTION, where_filter=WHERE_FILTER)
