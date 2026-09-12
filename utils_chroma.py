import chromadb
import ollama
    
####################
### BEG Config
####################

## NOTE: retrieval must use same model as embedding, otherwise the embeddings will not match and retrieval will fail
EMBEDDING_MODEL = "nomic-embed-text"  # "embeddinggemma:300m" # "qwen3-embedding:0.6b" # "nomic-embed-text" #

EMBEDDING_MODELS = {
    "nomic-embed-text": {
        "id": "nomic-embed-text"
        , "options": { "num_batch": 8192, "num_ctx": 8192}
        , "prompt_pfx_embed": "search_document: "
        , "prompt_pfx_query": "search_query: "
    },
    "embeddinggemma:300m": {
        "id": "embeddinggemma:300m"
        , "options": { "num_batch": 2048, "num_ctx": 2048}
        , "prompt_pfx_embed": "search_document: "
        , "prompt_pfx_query": "search_query: "
    },
    "qwen3-embedding:0.6b": {
        "id": "qwen3-embedding:0.6b"
        , "options": { "num_batch": 512, "num_ctx": 32768}
        , "prompt_pfx_embed": "search_document: "
        , "prompt_pfx_query": "search_query: "
    }
}

OUTPUT_COLLECTION = "pdf_data"
    
####################
### END Config
####################

def store_in_chromadb(documents, db_path="./chroma_db", collection_name=OUTPUT_COLLECTION):

    client = chromadb.PersistentClient(path=db_path)
    
    # Get or create the collection
    #TODO: fix/parameterize hardcoded stuff
    collection = client.get_or_create_collection(name=collection_name,    metadata={
        "hnsw:space": "l2",       # Distance function l2, cosine, ip
        "hnsw:construction_ef": 512,  # Accuracy vs speed during build 64 – 512
        "hnsw:search_ef": 128,        # Accuracy vs speed during query 10 – 128
        "hnsw:M": 64,                 # Max links per node 8 – 64
        "hnsw:batch_size": 100,       # Reindex batch size
        "hnsw:sync_threshold": 1000   # Disk sync element threshold
    })
    
    print(f"Embedding and storing {len(documents)} rows into ChromaDB...")
    
    for i, doc in enumerate(documents):

        if i % 100 == 0:
            print(f"Embedding and storing row {i+1}/{len(documents)}...")

        response = ollama.embeddings(model=EMBEDDING_MODELS[EMBEDDING_MODEL]["id"], prompt=EMBEDDING_MODELS[EMBEDDING_MODEL]["prompt_pfx_embed"] + doc["row"], options=EMBEDDING_MODELS[EMBEDDING_MODEL]["options"])

        embedding = response["embedding"]
        
        # Add the text, its vector embedding, and metadata to ChromaDB
        collection.add(
            ids=[f"row_{i}"],
            embeddings=[embedding],
            documents=[doc["row"]],
            metadatas=[doc["metadata"]]
        )
    print("Database successfully populated and saved locally!")


def get_query_from_chromadb(question, db_path="./chroma_db", collection_name=OUTPUT_COLLECTION, where_filter={}):
    """Queries ChromaDB for context and uses Ollama to generate an answer."""
    # Load the existing persistent database
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name=collection_name)
    collection.modify(metadata={"hnsw:search_ef": 50})

    # Embed the user's question using the same embedding model
    question_embedding_resp = ollama.embeddings(model=EMBEDDING_MODELS[EMBEDDING_MODEL]["id"], prompt=EMBEDDING_MODELS[EMBEDDING_MODEL]["prompt_pfx_query"] + question, options=EMBEDDING_MODELS[EMBEDDING_MODEL]["options"])

    question_embedding = question_embedding_resp["embedding"]
    
    # 2. Query ChromaDB for the top 3 most relevant table rows
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=100 #TODO: make parameter
        , where=where_filter
    )
    
    # Flatten retrieved documents into a single context string
    retrieved_docs = results.get("documents", [[]])[0]
    context = "\n".join(retrieved_docs)

    return context
