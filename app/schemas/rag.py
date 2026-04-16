from pydantic import BaseModel
from typing import List, Dict, Optional


class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    top_k: int = 5
    retrieval_top_k: int = 20


class RetrievedDocument(BaseModel):
    content: str
    score: Optional[float] = None
    metadata: Dict = {}


class QueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_documents: List[RetrievedDocument]
