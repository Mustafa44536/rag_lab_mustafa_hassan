from __future__ import annotations

from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
import os

import lancedb
from sentence_transformers import SentenceTransformer
from google import genai

load_dotenv()

DB_DIR = "knowledge_base"
TABLE_NAME = "transcripts"

@dataclass
class RetrievedChunk:
    source: str
    text: str
    score: float

class RAGChatbot:
    def __init__(self, top_k: int = 3) -> None:
        self.top_k = top_k
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GOOGLE_API_KEY in environment")

        # New Gemini SDK client
        self.client = genai.Client(api_key=api_key)

        self.db = lancedb.connect(DB_DIR)
        self.table = self.db.open_table(TABLE_NAME)

    def retrieve(self, query: str) -> List[RetrievedChunk]:
        qvec = self.embedder.encode(query).tolist()
        results = self.table.search(qvec).limit(self.top_k).to_list()

        chunks: List[RetrievedChunk] = []
        for r in results:
            chunks.append(
                RetrievedChunk(
                    source=r.get("source", ""),
                    text=r.get("text", ""),
                    score=float(r.get("_distance", 0.0)),
                )
            )
        return chunks

    def answer(self, question: str) -> str:
        chunks = self.retrieve(question)
        context = "\n\n".join([f"[{c.source}]\n{c.text}" for c in chunks])

        system_persona = (
            "You are a friendly Data Engineering YouTuber. "
            "Answer clearly and practically. "
            "Base your answer only on the provided context. "
            "If the context is not enough, say you don't know."
        )

        prompt = f"""{system_persona}

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        # Use a commonly available model name in the new SDK
        resp = self.client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt,
        )

        # resp.text is typically available; fallback to string conversion
        text = getattr(resp, "text", None)
        return (text if text else str(resp)).strip()
