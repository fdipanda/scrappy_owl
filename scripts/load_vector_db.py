import json
import chromadb
from tqdm import tqdm

INPUT_FILE = "data/embedded_chunks.json"

# Create persistent client
client = chromadb.PersistentClient(path="vector_db")

collection = client.get_or_create_collection(
    name="ksu_knowledge_base"
)

def main():

    with open(INPUT_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    for chunk in tqdm(chunks):

        try:
            collection.add(
                ids=[str(chunk["id"])],
                embeddings=[chunk["embedding"]],
                documents=[chunk["text"]],
                metadatas=[{
                    "title": chunk["title"],
                    "url": chunk["url"],
                    "category": chunk["category"],
                    "subcategory": chunk["subcategory"]
                }]
            )

        except Exception as e:
            print(f"Skipping chunk {chunk['id']}:", e)

    print("\nVector DB successfully saved to /vector_db")


if __name__ == "__main__":
    main()