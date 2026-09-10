import pdfplumber
import chromadb
import ollama

def find_tables_from_pdf(pdf_path):
    documents = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.find_tables()
            print(f"Page {page_num}: Found {len(tables)} tables.")
            for table in tables:

                headers = []
                for cell in table.rows[0].cells:
                    # cell format: (x0, y0, x1, y1)
                    if cell: 
                        # Extract text within these exact bounds
                        text = page.within_bbox(cell).extract_text()
                        headers.append({
                            "text": text.strip() if text else "",
                            "x0": cell[0],
                            "x1": cell[2]
                        })

                data_rows = []
                for row in table.rows[1:]:  # Limit to first 25 rows for testing purposes
                    row_data = {"menu_item": ""}
                    for cell in row.cells:
                        if cell:
                            cell_x0, cell_x1 = cell[0], cell[2]
                            cell_text = page.within_bbox(cell).extract_text()
                            cell_text = cell_text.strip() if cell_text else ""

                            row_data["menu_item"] = row_data[ headers[0]["text"] ] if headers[0]["text"] in row_data else "" # Default to first header for menu item

                            """
                            # NOTE: this is specific to the PDF structure and may need adjustment for other PDFs
                            if(cell_text == headers[1]["text"]): 
                                data_rows.pop()  # Remove the last row if it matches the header text
                                # TODO: capture headers[0] as a new category for the next rows until the next header is found
                                break  # Skip if the cell text matches a header
                            """
                            
                            # Find which header column this cell falls under
                            matched_header = "Unknown"
                            for header in headers:
                                # Check if the cell horizontally overlaps or aligns with the header
                                # Allowing a small 2-point tolerance for slight PDF alignment imperfections
                                if cell_x0 >= (header["x0"] - 2) and cell_x1 <= (header["x1"] + 2):
                                    matched_header = header["text"]
                                    break
                            
                            row_data[matched_header] = cell_text

                    data_rows.append(row_data)
                    #print(f"Extracted Row Data: {row_data}")

                for row in data_rows:
                    # Filter out None values and clean up whitespaces
                    cleaned_row = row # [str(cell).strip() for cell in row if cell is not None] # 
                    if cleaned_row:
                        # Join row elements with a pipe delimiter for structured text representation
                        row_text = str(cleaned_row) #  " | ".join(cleaned_row) # str(cleaned_row).replace("',", "'|") # 
                        #print(f"Extracted Row: {row_text}")
                        documents.append({
                            "text": row_text,
                            "metadata": {"page": page_num, "source": pdf_path}
                        })

    return documents

def extract_tables_from_pdf(pdf_path):
    """Extracts tables from a PDF and converts rows into clean string formats."""
    documents = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Filter out None values and clean up whitespaces
                    cleaned_row = [str(cell).strip() for cell in row if cell is not None]
                    if cleaned_row:
                        # Join row elements with a pipe delimiter for structured text representation
                        row_text = " | ".join(cleaned_row)
                        documents.append({
                            "text": row_text,
                            "metadata": {"page": page_num, "source": pdf_path}
                        })
    return documents

def store_in_chromadb(documents, db_path="./chroma_db", collection_name="pdf_tables"):

    client = chromadb.PersistentClient(path=db_path)
    
    # Get or create the collection
    collection = client.get_or_create_collection(name=collection_name,    metadata={
        "hnsw:space": "l2",       # Distance function l2, cosine, ip
        "hnsw:construction_ef": 512,  # Accuracy vs speed during build 64 – 512
        "hnsw:search_ef": 128,         # Accuracy vs speed during query 10 – 128
        "hnsw:M": 64,                 # Max links per node 8 – 64
        "hnsw:batch_size": 100,       # Reindex batch size
        "hnsw:sync_threshold": 1000   # Disk sync element threshold
    })
    
    print(f"Embedding and storing {len(documents)} rows into ChromaDB...")
    
    for i, doc in enumerate(documents):

        model = "embeddinggemma:300m" # "qwen3-embedding:0.6b" # "nomic-embed-text" # 
        response = ollama.embeddings(model="qwen3-embedding:0.6b", prompt="search_document: " + doc["text"], options ={ "num_batch": 512, "num_ctx": 32768})
        #response = ollama.embeddings(model="embeddinggemma:300m", prompt="search_document: " + doc["text"], options ={ "num_batch": 2048, "num_ctx": 2048})
        #response = ollama.embeddings(model="nomic-embed-text", prompt="search_document: " + doc["text"], options ={ "num_batch": 8192, "num_ctx": 8192})

        embedding = response["embedding"]
        
        # Add the text, its vector embedding, and metadata to ChromaDB
        collection.add(
            ids=[f"row_{i}"],
            embeddings=[embedding],
            documents=[doc["text"]],
            metadatas=[doc["metadata"]]
        )
    print("Database successfully populated and saved locally!")

# --- Execution ---
if __name__ == "__main__":
    # Replace with the path to your local PDF file
    PDF_FILE_PATH = "Chilis Nutrition Menu Generic.pdf" 
    
    # 1. Parse PDF
    #extracted_data = extract_tables_from_pdf(PDF_FILE_PATH)
    extracted_data = find_tables_from_pdf(PDF_FILE_PATH)
    
    # 2. Store vector data locally
    if extracted_data:
        store_in_chromadb(extracted_data)
    else:
        print("No tabular data found in the PDF.")
