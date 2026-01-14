from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel

from backend.rag import chat

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/rag/query")
def rag_query(req: QueryRequest):
    return chat(req.question)
