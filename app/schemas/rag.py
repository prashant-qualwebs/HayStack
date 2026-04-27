from pydantic import BaseModel
from typing import List
from app.core.config import settings


class QueryRequest(BaseModel):
    query: str
    user_id: str
    top_k: int = settings.DEFAULT_QUERY_TOP_K


class RetrievedDocument(BaseModel):
    content: str
    score: float | None = None


class QueryResponse(BaseModel):
    query: str
    retrieved_documents: List[RetrievedDocument]
