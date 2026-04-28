import ollama
from chromadb import PersistentClient


client = PersistentClient(path="vector_db")
collection = client.get_or_create_collection("ksu_knowledge_base")

SYSTEM_PROMPT = ("You are Scrappy Bot, a helpful university assistant with a passion for helping freshman students find and understand the information they're looking for.\n"
                 "Below, you will be given several chunks of data followed by a query from a university student."
                 "Your job is to answer the question clearly using only those chunks of data. \n"
                 "If the question cannot be sufficiently answered using only those chunks, then your response MUST include an apology for being unable to answer the question followed by the reason you are unable to answer it.")

def embed_query(question: str) -> list:
    # old Ollama API. Use .embed()
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=question
    )
    return response["embedding"]

def retrieve_chunks(question: str, max_distance, n_results=5) -> list[dict]:
    query_vector = embed_query(question)
    query_results = collection.query(
        query_embeddings=query_vector,
        n_results = n_results
    )

    results = []
    for text, metadata, distance in zip(query_results["documents"][0], query_results["metadatas"][0], query_results["distances"][0]):
        results.append({
            "text": text,
            "metadata": metadata,
            "distance": distance
        })

    #Filter results based on distance (shorter distance = more relevant)
    results = [r for r in results if r["distance"] <= max_distance]

    return results

def format_chunks(query_results: list[dict]) -> str:
    prompt = ""
    for i in range(len(query_results)):
        prompt += f"Title: {query_results[i]['metadata']['title']}\n"
        prompt += f"Category: {query_results[i]['metadata']['category']}\n"
        prompt += f"url: {query_results[i]['metadata']['url']}\n"
        prompt += (f"text: {query_results[i]['text']}\n"
                   f"------------------------------------------------------\n")
    return prompt

def build_messages(question: str, context: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
    }]

def build_messages_no_context(question: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "No relevant content was found in the database for this question\n\n"
                       f"Question: {question}"
        }
    ]

def generate(messages: list[dict]) -> str:
    response = ollama.chat(
        model = 'phi3:latest',
        messages=messages,
        options={
            'temperature': 0.3,
            'num_predict': 500
        }
    )
    return response['message']['content']

def generate_stream(messages: list[dict]) -> str:
    stream = ollama.chat(
        model="phi3:latest",
        messages=messages,
        stream=True,
        options = {
            'temperature': 0.3,
            'num_predict': 500
        }
    )
    full_response = ""
    for chunk in stream:
        token = chunk['message']['content']
        full_response += token
        print(token, end='', flush=True)
    print()
    return full_response

def ask(question: str, n_results: int=5, max_distance: float = 350) -> dict:

    chunks = retrieve_chunks(question, max_distance, n_results)

    if chunks:
        context = format_chunks(chunks)
        messages = build_messages(question,context)
    else:
        messages = build_messages_no_context(question)

    answer = generate(messages)

    return{
        "answer": answer,
        "sources": [{
            "Title": chunk['metadata']['title'],
            "url": chunk['metadata']['url'],
            "Category": chunk['metadata']['category'],
            "Text": chunk['text']
        } for chunk in chunks],
        "chunks_used": len(chunks),
        "question": question
    }

def print_result(question: str):
    response = ask(question)
    num_sources = len(response["sources"])


    print("=========================\n"
          f"QUESTION: {question}\n"
          f"CHUNKS USED: {num_sources}\n"
          f"SOURCES:\n")
    for i, source in enumerate(response["sources"], start=1):
        print(f"    {i}: [{source["Category"]}] {source["Title"]} — {source["url"]}\n"
              f"    TEXT: {source["Text"]}\n")
    print(f"ANSWER: {response["answer"]}\n"
          f"=========================\n")

    return


def main():
    questions = [
        "Who won the super bowl?",
        "What dining options are on campus?",
        "Do you eat ass?",
        "Bitch whore cunt ass balls"
    ]
    for i in questions:
        print_result(i)




if __name__ == "__main__":
    main()




