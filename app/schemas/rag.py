from typing import Any, Dict, List

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    document_id: str | None = None


class RetrievedDocument(BaseModel):
    content: str
    score: float | None = None
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    query: str
    retrieved_documents: List[RetrievedDocument]
