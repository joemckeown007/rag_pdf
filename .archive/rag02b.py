# Import necessary libraries
import chromadb
import ollama
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

ollama_ef = OllamaEmbeddingFunction(
    url="http://localhost:11434", model_name="nomic-embed-text", 
)

# Initialize ChromaDB client and collection (assuming it's already set up and populated from Part 1)
chroma_client = chromadb.PersistentClient(path="./",)
#collection = chroma_client.get_or_create_collection(name="document_collection", embedding_function=ollama_ef )
collection = chroma_client.get_or_create_collection(name="document_collection", embedding_function=ollama_ef)

# Step 1: Function to query ChromaDB with a prompt
def query_chromadb(prompt, n_results=3):
    q1_embed = ollama.embeddings(model="nomic-embed-text", prompt=prompt)
    #q1 = collection.query(query_embeddings=[q1_embed["embedding"]], n_results=3)

    results = collection.query(
        #query_embeddings=[q1_embed["embedding"]],
        query_texts=[prompt],  # User's query
        n_results=n_results,   # Number of relevant chunks to retrieve
        include=["documents", "metadatas"]  # Retrieve both document text and metadata
    )
    return results

# Step 2: Flattening functions for retrieved documents and metadata
def flatten_documents(documents):
    return [sentence for doc in documents for sentence in doc]

def flatten_metadatas(metadatas):
    return [meta for meta_list in metadatas for meta in meta_list]

# Example query and flattening
prompt = "Which items have cheese?"  # User's question
chromadb_results = query_chromadb(prompt)
flat_chunks = flatten_documents(chromadb_results["documents"])
flat_metadata = flatten_metadatas(chromadb_results["metadatas"])

# Join the retrieved chunks with delimiters and metadata
# retrieved_chunks = [f"{chunk} (Source: {meta['page']})" for chunk, meta in zip(flat_chunks, flat_metadata)]
retrieved_chunks = [f"{chunk}" for chunk in flat_chunks]
full_retrieved_chunks = "\n\n---\n\n".join(retrieved_chunks)

# Step 3: Define the system prompt and generate a response using Ollama’s Llama 3.1
SYSTEM_PROMPT = """
You are a helpful assistant answering questions based on the provided context only.
Use the retrieved information and reference sources accurately.
"""

def generate_answer(prompt, retrieved_chunks):
    response = ollama.chat(
        model="gemma4:e2b-it-qat", # llama3.2 or gemma4:e2b-it-qat
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},  # Instructional prompt for the model
            {"role": "user", "content": f"{retrieved_chunks}\n\nAnswer this question: {prompt}"}  # Combined context and user prompt
        ]
    )["message"]["content"]
    return response

# Generate and print the answer
answer = generate_answer(prompt, full_retrieved_chunks)
print("Generated Response:")
print(answer)

# Generate Answer when running the script
# Generated Response:
# According to the context, Chain Of Thought / Step by Step refers to the process where you ask the AI to generate a list of steps as to how it came to its conclusion. This allows you to understand why the AI generated a particular response.
# Source: Page 90 (Prompt Engineering Playbook)