from fastapi import FastAPI
from pydantic import BaseModel

from backend.rag import RAGChatbot

app = FastAPI(title="RAG API")

bot = RAGChatbot(top_k=3)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/rag/query", response_model=QueryResponse)
def rag_query(req: QueryRequest):
    answer = bot.answer(req.question)
    return {"answer": answer}
