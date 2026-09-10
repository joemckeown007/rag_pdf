import ollama
import utils_chroma as uc

####################
### BEG Config
####################

DATA_IN_PFX = "./data/in/"
DATA_OUT_PFX = "./data/out/"

QUERY_COLLECTION = "pdf_data"

USER_QUESTION = "Which item has the most fat calories?" 
USER_QUESTION = "Find all the nacho items and then rank them from the least to most calories. Be aware of the same menu item may have different portion sizes." 
USER_QUESTION = "How many menu items are there total?" 
USER_QUESTION = "How many cals are in the menu item 'Fudge Brownie'?" 
USER_QUESTION = "How much prot in the Fudge Brownie?" 
USER_QUESTION = "List all the menu items that have more than 1000 calories." 
USER_QUESTION = "How much does 'WINGS OVER BUFFALO' cost?" 
USER_QUESTION = "What are the options for the Create Your Own Combo?" 
USER_QUESTION = "What is the most expensive steak?"
USER_QUESTION = "Which items have cheese in their names?"

####################
### END Config
####################

query_db_path = DATA_OUT_PFX + "chroma_db"

def answer_question_from_db(question, db_path=query_db_path, collection_name=QUERY_COLLECTION):

    context = uc.get_query_from_chromadb(question, db_path=db_path, collection_name=collection_name)
    
    if not context.strip():
        print("No relevant context found in the database.")
        return
    
    # 3. Construct the prompt for the Chat Model
    system_prompt = (
        "You are an AI assistant answering questions based strictly on the provided table data context. "
        "If the answer cannot be found in the context, say that you do not know."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    # Generate response using Ollama chat (using llama3 as an example)
    print("\nThinking...")
    response = ollama.chat(
        model="llama3.2", # llama3.2 or gemma4:e2b-it-qat
        options={"temperature": 0.0}, # 0 should give most deterministic responses
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
    answer_question_from_db(USER_QUESTION, db_path=query_db_path, collection_name=QUERY_COLLECTION)
