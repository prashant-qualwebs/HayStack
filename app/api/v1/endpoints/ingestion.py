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

        ingestible_chunks = [
            chunk
            for chunk in chunks
            if chunk.text and chunk.text.strip()
        ]
        if not ingestible_chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks with non-empty text provided",
            )

        count = ingest_chunks(ingestible_chunks)

        return IngestResponse(
            message="Chunks ingested successfully",
            documents_count=count,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
