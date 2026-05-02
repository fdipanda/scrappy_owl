from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import ask


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str
    n_results: int = 5
    max_distance: float = 350.0

@app.post("/ask")
def handle_ask(request: AskRequest):
    return ask(**request.model_dump())

@app.get("/health")
def health():
    return {"status": "ok"}
