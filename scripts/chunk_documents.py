import json
import re
from tqdm import tqdm

INPUT_FILE = "data/documents.json"
OUTPUT_FILE = "data/chunks.json"

CHUNK_SIZE = 220
OVERLAP = 40

SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_text(text):

    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def split_paragraphs(text):

    parts = re.split(r"\n\s*\n+", text)

    return [normalize_text(part) for part in parts if normalize_text(part)]


def split_sentences(text):

    sentences = SENTENCE_BOUNDARY_RE.split(text)

    return [normalize_text(sentence) for sentence in sentences if normalize_text(sentence)]


def split_oversized_text(text, chunk_size):

    sentences = split_sentences(text)

    if len(sentences) <= 1:
        words = text.split()
        return [
            " ".join(words[index:index + chunk_size])
            for index in range(0, len(words), chunk_size)
        ]

    chunks = []
    current = []
    current_len = 0

    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_len = len(sentence_words)

        if sentence_len > chunk_size:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0

            chunks.extend(split_oversized_text(sentence, chunk_size))
            continue

        if current_len and current_len + sentence_len > chunk_size:
            chunks.append(" ".join(current))
            current = []
            current_len = 0

        current.append(sentence)
        current_len += sentence_len

    if current:
        chunks.append(" ".join(current))

    return chunks


def overlap_tail(text, overlap):

    words = text.split()

    if overlap <= 0 or len(words) <= overlap:
        return text

    return " ".join(words[-overlap:])


def chunk_text(text):

    paragraphs = split_paragraphs(text)

    chunks = []
    current_parts = []
    current_len = 0

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        paragraph_len = len(paragraph_words)

        if paragraph_len > CHUNK_SIZE:
            oversized_chunks = split_oversized_text(paragraph, CHUNK_SIZE)

            for oversized_chunk in oversized_chunks:
                if current_parts:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_len = 0

                chunks.append(oversized_chunk)

                if OVERLAP > 0:
                    current_parts = [overlap_tail(oversized_chunk, OVERLAP)]
                    current_len = len(current_parts[0].split())

            continue

        if current_len and current_len + paragraph_len > CHUNK_SIZE:
            chunks.append("\n\n".join(current_parts))

            overlap_text = overlap_tail(chunks[-1], OVERLAP)
            current_parts = [overlap_text] if overlap_text else []
            current_len = len(overlap_text.split()) if overlap_text else 0

        current_parts.append(paragraph)
        current_len += paragraph_len

    if current_parts:
        chunks.append("\n\n".join(current_parts))

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
