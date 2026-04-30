import json
import re

import requests
from bs4 import BeautifulSoup
from readability import Document
from tqdm import tqdm

INPUT_FILE = "data/seed_urls.json"
OUTPUT_FILE = "data/documents.json"

BLOCK_TAGS = {
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "ol",
    "p",
    "table",
    "td",
    "th",
    "tr",
    "ul"
}

BOILERPLATE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"^apply now$",
        r"^apply today!?$",
        r"^get info$",
        r"^visit site$",
        r"^learn more$",
        r"^see the list$",
        r"^submit a concern$",
        r"^take a virtual tour$",
        r"^view undergraduate link programs$",
        r"^request information$",
        r"^skip to main content$",
        r"^back to top$",
    ]
]

def extract_urls(data):

    pages = []

    def walk(category, value, path=None):

        path = path or []

        if isinstance(value, list):
            for url in value:
                if url:
                    pages.append({
                        "category": category,
                        "subcategory": " > ".join(path) if path else "main",
                        "url": url
                    })
            return

        if isinstance(value, dict):
            for key, nested_value in value.items():
                next_path = path if key == "main" else path + [key]
                walk(category, nested_value, next_path)

    for category, value in data.items():
        walk(category, value)

    return pages


def normalize_text(text):

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def is_boilerplate(text):

    return any(pattern.match(text) for pattern in BOILERPLATE_PATTERNS)


def extract_paragraphs(soup):

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    paragraphs = []
    seen = set()

    for tag in soup.find_all(BLOCK_TAGS):
        text = normalize_text(tag.get_text(" ", strip=True))

        if not text or text in seen or is_boilerplate(text):
            continue

        paragraphs.append(text)
        seen.add(text)

    return paragraphs

def clean_page(url):

    try:
        response = requests.get(url, timeout=10)
        html = response.text

        doc = Document(html)

        article_html = doc.summary()

        soup = BeautifulSoup(article_html, "html.parser")
        paragraphs = extract_paragraphs(soup)
        text = "\n\n".join(paragraphs)

        title = doc.title().split("|")[0].strip()

        return {
            "url": url,
            "title": title,
            "text": text
        }

    except Exception as e:
        print("Failed:", url, e)
        return None


def main():

    with open(INPUT_FILE) as f:
        raw_data = json.load(f)

    pages = extract_urls(raw_data)
    documents = []
    for page in tqdm(pages):

        url = page["url"]
        category = page["category"]
        subcategory = page["subcategory"]

        data = clean_page(url)

        if data:

            data["category"] = category
            data["subcategory"] = subcategory

            documents.append(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
