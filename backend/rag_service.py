from __future__ import annotations

from backend.rag import chat

def answer_question(question: str) -> dict:
    """
    Samma output som FastAPI /rag/query.
    Delegaterar till backend.rag.chat().
    """
    return chat(question)
