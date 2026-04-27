from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.ingestion import IngestChunk, IngestResponse
from app.services.ingestion_service import ingest_chunks

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(chunks: List[IngestChunk]):
    try:
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks provided")

        empty_chunks = [
            chunk.chunk_index
            for chunk in chunks
            if not chunk.text or not chunk.text.strip()
        ]
        if empty_chunks:
            raise HTTPException(
                status_code=400,
                detail=f"Chunk text cannot be empty. Empty chunk_index values: {empty_chunks}",
            )

        count = ingest_chunks(chunks)

        return IngestResponse(
            message="Chunks ingested successfully",
            documents_count=count,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
