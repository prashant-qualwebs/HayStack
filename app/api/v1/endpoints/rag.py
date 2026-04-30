from fastapi import APIRouter, HTTPException
from app.schemas.rag import QueryRequest, QueryResponse
from app.services.hybrid_rag_service import retrieve_and_generate

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        if not request.user_id.strip():
            raise HTTPException(status_code=400, detail="user_id cannot be empty")

        result = retrieve_and_generate(
            query=request.query,
            document_id=request.document_id,
            user_id=request.user_id,
        )
        return QueryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
