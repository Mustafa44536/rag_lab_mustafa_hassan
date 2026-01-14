from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
import lancedb
from sentence_transformers import SentenceTransformer
from pydantic_ai import Agent

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = str(BASE_DIR / "knowledge_base")
TABLE_NAME = "transcripts"

# Lazy singletons
_embedder: Optional[SentenceTransformer] = None
_table = None

def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def _get_table():
    global _table
    if _table is None:
        db = lancedb.connect(DB_DIR)
        _table = db.open_table(TABLE_NAME)
    return _table

# Agent (uses env var GOOGLE_API_KEY automatically)
rag_agent = Agent(
    model="google-gla:models/gemini-flash-latest",
    retries=1,
    system_prompt=(
        "You are The Youtuber - a friendly Data Engineering educator. "
        "Answer based ONLY on the provided retrieved context. "
        "If context is insufficient, say you don't know. "
        "Max 5 sentences. Always mention which source file(s) you used."
    ),
)

@rag_agent.tool_plain
def retrieve_top_documents(query: str, k: int = 3) -> str:
    """
    Vector search in LanceDB (uses embeddings stored in 'vector' column).
    """
    table = _get_table()
    embedder = _get_embedder()
    qvec = embedder.encode(query).tolist()

    results = table.search(qvec).limit(k).to_list()
    if not results:
        return "No matches found in the knowledge base."

    blocks: List[str] = []
    for r in results:
        src = r.get("source", "")
        text = r.get("text", "")
        blocks.append(f"SOURCE: {src}\n{text}")
    return "\n\n---\n\n".join(blocks)

def chat(question: str) -> dict:
    prompt = (
        "Use the tool retrieve_top_documents to fetch context, then answer.\n\n"
        f"QUESTION: {question}"
    )
    result = rag_agent.run_sync(prompt)
    return {"question": question, "answer": result.output}
