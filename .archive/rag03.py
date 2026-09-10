import os
import pdfplumber
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize ChromaDB client and embedding function
# Using a lightweight, high-performing open-source embedding model
chroma_client = chromadb.PersistentClient(path="./")
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2" # nomic-embed-text # all-MiniLM-L6-v2
)

# Create or get a collection for your PDF tables
collection = chroma_client.get_or_create_collection(
    name="pdf_tables", 
    embedding_function=embedding_model
)

# Path to your PDF file
pdf_path = "Chilis Nutrition Menu Generic.pdf"

# 2. Extract tables using pdfplumber
extracted_rows = []

if os.path.exists(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables, start=1):
                # Clean up empty rows/cols and format as text strings
                for row_idx, row in enumerate(table):
                    # Filter out None values and join row items with a separator
                    row_data = [str(cell).strip() if cell is not None else "" for cell in row]
                    row_text = " | ".join(row_data)
                    
                    # Create a unique ID for each row chunk
                    chunk_id = f"page_{page_num}_table_{table_num}_row_{row_idx}"
                    
                    # Keep metadata to trace the source of the answer later
                    metadata = {
                        "page_number": page_num,
                        "table_number": table_num,
                        "row_index": row_idx,
                        "source": os.path.basename(pdf_path)
                    }
                    
                    # Add to our batch list if the row contains actual text
                    if row_text.strip(" |"):
                        extracted_rows.append({
                            "id": chunk_id,
                            "text": row_text,
                            "metadata": metadata
                        })
    
    # 3. Embed and upsert data into ChromaDB
    if extracted_rows:
        collection.upsert(
            ids=[item["id"] for item in extracted_rows],
            documents=[item["text"] for item in extracted_rows],
            metadatas=[item["metadata"] for item in extracted_rows]
        )
        print(f"Successfully embedded {len(extracted_rows)} table rows into ChromaDB.")
    else:
        print("No tables or row data found in the PDF.")
else:
    print(f"Please replace '{pdf_path}' with a valid PDF file path.")

# 4. Example Query: Retrieve the closest matching table data
query_text = "Which items have cheese?"
results = collection.query(
    query_texts=[query_text],
    n_results=20  # Top 2 closest matches
)

print("\n--- Query Results ---")
for doc, meta, score in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
    print(f"Match (Distance: {score:.4f}):")
    print(f"Content: {doc}")
    print(f"Source: Page {meta['page_number']}, Table {meta['table_number']}\n")
