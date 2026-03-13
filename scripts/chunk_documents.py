import json
from tqdm import tqdm

INPUT_FILE = "data/documents.json"
OUTPUT_FILE = "data/chunks.json"

CHUNK_SIZE = 400
OVERLAP = 50


def chunk_text(text):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + CHUNK_SIZE

        chunk = words[start:end]

        chunks.append(" ".join(chunk))

        start += CHUNK_SIZE - OVERLAP

    return chunks


def main():

    with open(INPUT_FILE, encoding="utf-8") as f:
        documents = json.load(f)

    chunks = []

    chunk_id = 0

    for doc in tqdm(documents):

        text_chunks = chunk_text(doc["text"])

        for c in text_chunks:

            chunks.append({
                "id": chunk_id,
                "text": c,
                "title": doc["title"],
                "url": doc["url"],
                "category": doc["category"],
                "subcategory": doc["subcategory"]
            })

            chunk_id += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()