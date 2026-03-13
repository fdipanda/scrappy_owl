import json
import requests
from bs4 import BeautifulSoup
from readability import Document
from tqdm import tqdm

INPUT_FILE = "data/seed_urls.json"
OUTPUT_FILE = "data/documents.json"

def extract_urls(data):

    pages = []

    for category, value in data.items():

        if isinstance(value, list):

            for url in value:
                if url:
                    pages.append({
                        "category": category,
                        "subcategory": "main",
                        "url": url
                    })

        elif isinstance(value, dict):

            for subcategory, urls in value.items():
                for url in urls:
                    if url:
                        pages.append({
                            "category": category,
                            "subcategory": subcategory,
                            "url": url
                        })

    return pages

def clean_page(url):

    try:
        response = requests.get(url, timeout=10)
        html = response.text

        doc = Document(html)

        article_html = doc.summary()

        soup = BeautifulSoup(article_html, "html.parser")

        text = soup.get_text(separator=" ", strip=True)

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