import time
import ollama
import chromadb

documents = [
    "Open-Meteo is a free weather API that needs no API key.",
    "The Cat Facts API returns random facts about cats as JSON.",
    "DeepSeek offers a low-cost, OpenAI-compatible chat API.",
    "The REST Countries API returns country data like capitals and currencies.",
]

client = chromadb.Client()
collection = client.create_collection(name="docs")

for i, doc in enumerate(documents):
    vector = ollama.embeddings(model="nomic-embed-text", prompt=doc)["embedding"]
    collection.add(ids=[str(i)], embeddings=[vector], documents=[doc])

print("Stored", collection.count(), "documents.")

question = "Is there a plastic building in legoland?"
question = "Which API gives weather data for free?"

q_vector = ollama.embeddings(model="nomic-embed-text", prompt=question)["embedding"]
results = collection.query(query_embeddings=[q_vector], n_results=2)
context = "\n".join(results["documents"][0])

print("Retrieved context:\n", context)

prompt = f"""Answer the question using only the context below.
If the answer is not in the context, say you do not know.

Context:
{context}

Question: {question}
"""

print(f"Question to be answered:\n{question}")

#####################
start = time.time()

# llama3.2:latest
print("llama3.2")
response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
print(response["message"]["content"])

end = time.time()
print(f"Time elapsed: {int(end - start)} seconds")
#####################

#####################
start = time.time()

print("gemma4:e2b-it-qat")
response = ollama.chat(model="gemma4:e2b-it-qat", messages=[{"role": "user", "content": prompt}])
print(response["message"]["content"])

end = time.time()
print(f"Time elapsed: {int(end - start)} seconds")
#####################

