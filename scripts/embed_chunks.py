import json
import ollama
from tqdm import tqdm

INPUT_FILE = "data/chunks.json"
OUTPUT_FILE = "data/embedded_chunks.json"


def embed_text(text):

    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )

    return response["embedding"]


def main():

    with open(INPUT_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    embedded_chunks = []

    for chunk in tqdm(chunks):

        embedding = embed_text(chunk["text"])

        chunk["embedding"] = embedding

        embedded_chunks.append(chunk)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(embedded_chunks, f, indent=2)


if __name__ == "__main__":
    main()