import chromadb
import ollama

def answer_question_from_db(question, db_path="./chroma_db", collection_name="pdf_tables"):
    context = """
## Table name: embeddings_queue

## Table schema

cid|name|type|notnull|dflt_value|pk
0|seq_id|INTEGER|0|1
1|created_at|TIMESTAMP|1|CURRENT_TIMESTAMP|0
2|operation|INTEGER|1||0
3|topic|TEXT|1||0
4|id|TEXT|1||0
5|vector|BLOB|0||0
6|encoding|TEXT|0||0
7|metadata|TEXT|0||0
"""
    
    # 3. Construct the prompt for the Chat Model
    system_prompt = (
        "You are a SQL assistant that helps users query a local SQLite database using natural language."
        "If the answer cannot be found in the context, say that you do not know."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    # Generate response
    print("\nThinking...")
    response = ollama.chat(
        model="gemma4:e2b-it-qat", # llama3.2 or gemma4:e2b-it-qat
        messages=[
            {"role": "system", "content": system_prompt}, # TODO: learn about these roles
            {"role": "user", "content": user_prompt}
        ]
    )
    
    #print(f"\n[Retrieved Context Used]:\n{context}\n")
    print(f"[AI Response]:\n{response['message']['content']}")

# --- Execution ---
if __name__ == "__main__":

    USER_QUESTION = "List all the menu items that have more than 1000 calories." 
    USER_QUESTION = "I want to find the latest 2 entries in the embeddings_queue table. Please provide the SQL query to do that." 
    USER_QUESTION = "I want to find all entries in the embeddings_queue table that have the word 'cheese' in their 'metadata' column. Please provide the SQL query to do that." 
       
    print(f"User Question: {USER_QUESTION}")
    answer_question_from_db(USER_QUESTION)
