from pydantic import BaseModel
from typing import List, Dict, Optional
from app.core.config import settings


class QueryRequest(BaseModel):
    query: str
    user_id: str
    top_k: int = settings.DEFAULT_QUERY_TOP_K


class RetrievedDocument(BaseModel):
    content: str
    score: Optional[float] = None
    metadata: Dict = {}


class QueryResponse(BaseModel):
    query: str
    retrieved_documents: List[RetrievedDocument]
