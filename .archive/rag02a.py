# Import necessary libraries
import pdfplumber
import chromadb

# Define the PDF file path
pdf_path = 'Chilis Nutrition Menu Generic.pdf'

# Lists to store extracted chunks and metadata
chunks = []
metadata = []

with pdfplumber.open(pdf_path) as pdf:
    #for page_num, page in pdf.pages:
    for page_num, page in enumerate(pdf.pages, start=1):
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                if row:  # Only store pages with text
                    print(row)
                    chunks.append(str(row))  # Add extracted text to chunks
                    metadata.append({"page": f"Page {page_num}"})  # Store the page number as metadata

"""
# Step 1: Extract text from PDF
with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        if text:  # Only store pages with text
            chunks.append(text)  # Add extracted text to chunks
            metadata.append({"page": f"Page {page_num}"})  # Store the page number as metadata
"""




# Step 2: Initialize ChromaDB client and create a collection
chroma_client = chromadb.PersistentClient(path="./")  # Set up ChromaDB with local storage
collection = chroma_client.get_or_create_collection(name="document_collection")

# Step 3: Upsert (insert or update) the extracted data with metadata into ChromaDB
def upsert_into_chromadb(chunks, metadata):
    collection.add(
        documents=chunks,                # List of text chunks to store
        metadatas=metadata,              # Corresponding metadata for each chunk
        ids=[f"page_{i+1}" for i in range(len(chunks))]  # Generate unique IDs for each page
    )

# Store extracted chunks and metadata in ChromaDB
upsert_into_chromadb(chunks, metadata)
print("Data successfully stored in ChromaDB.")