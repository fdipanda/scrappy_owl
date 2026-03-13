# Scrappy Owl — KSU Website Chatbot

## Overview

Scrappy Owl is a chatbot designed to answer questions about **Kennesaw State University** using information from the official KSU website.

The project uses a **Retrieval-Augmented Generation (RAG)** approach. Instead of relying only on a language model, the system retrieves relevant information from a knowledge base built from KSU webpages.

So far, this repository contains the **data pipeline used to build the knowledge base**.

Later, this database will be connected to a **Phi-3 model running locally through Ollama** to generate answers.

## Current Pipeline

The system currently performs the following steps:

URLs  
↓  
Scrape website pages  
↓  
Clean and extract text  
↓  
Split text into chunks  
↓  
Generate embeddings  
↓  
Store embeddings in a vector database  

This vector database will later be used for retrieval during chatbot conversations.

## Project Structure

scrappy_owl/

data/  
  seed_urls.json  
  documents.json  
  chunks.json  
  embedded_chunks.json  

scripts/  
  scrape_pages.py  
  chunk_documents.py  
  embed_chunks.py  
  load_vector_db.py  

vector_db/

requirements.txt  
README.md

## Pipeline Steps

### 1. Collect URLs

Important KSU webpages are stored in:

data/seed_urls.json

These URLs are organized by category (Admissions, Student Life, etc.).

### 2. Scrape Website Pages

Script:

scripts/scrape_pages.py

This script downloads the webpages and extracts the main readable content.

Output:

data/documents.json


### 3. Chunk the Text

Script:

scripts/chunk_documents.py

Large pages are split into smaller pieces to improve search and retrieval.

Output:

data/chunks.json


### 4. Generate Embeddings

Script:

scripts/embed_chunks.py

Each chunk is converted into a vector embedding using the Ollama model:

nomic-embed-text

Output:

data/embedded_chunks.json


### 5. Build the Vector Database

Script:

scripts/load_vector_db.py

This loads the embeddings into a **Chroma vector database** stored in:

vector_db/

This database allows the system to retrieve the most relevant information for a user’s question.

## Running the Pipeline

Activate the virtual environment:

venv\Scripts\activate

Run the scripts in order:

python scripts/scrape_pages.py  
python scripts/chunk_documents.py  
python scripts/embed_chunks.py  
python scripts/load_vector_db.py


## Next Step

The next phase of the project will connect the vector database to a **Phi-3 model through Ollama**, allowing the chatbot to:

1. Receive a user question  
2. Retrieve relevant chunks from the database  
3. Send that context to the LLM  
4. Generate an answer  


## Contributors

Franck Alexis  
Michael Collins
Erick Smith