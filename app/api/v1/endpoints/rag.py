from fastapi import APIRouter
from app.schemas.rag import QueryRequest, QueryResponse
from app.services.hybrid_rag_service import retrieve_and_generate_hybrid
from app.core.exceptions import ValidationError, ProcessingError

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    if not request.query.strip():
        raise ValidationError("Query cannot be empty")
    
    try:
        result = retrieve_and_generate_hybrid(request.query, request.user_id, request.top_k, request.retrieval_top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise ProcessingError(f"Query failed: {str(e)}")
