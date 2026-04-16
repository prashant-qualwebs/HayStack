from pydantic import BaseModel
from typing import List, Dict, Optional
from app.core.config import settings


class QueryRequest(BaseModel):
    query: str
    user_id: str = settings.DEFAULT_USER_ID
    top_k: int = settings.RERANK_TOP_K
    retrieval_top_k: int = settings.RETRIEVAL_TOP_K


class RetrievedDocument(BaseModel):
    content: str
    score: Optional[float] = None
    metadata: Dict = {}


class QueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_documents: List[RetrievedDocument]
