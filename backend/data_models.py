from pydantic import BaseModel
from typing import List

class RagQuery(BaseModel):
    question: str

class SourceChunk(BaseModel):
    source: str
    text: str
    score: float

class RagResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
