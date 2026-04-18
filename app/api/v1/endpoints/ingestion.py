from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from app.schemas.ingestion import IngestResponse
from app.services.ingestion_service import ingest_files

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    files: List[UploadFile] = File(...),
    user_id: str = Form(...),
    document_id: str = Form(...)
):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types
        allowed_extensions = {".pdf", ".docx", ".doc"}
        for file in files:
            file_ext = file.filename.lower().split(".")[-1]
            if f".{file_ext}" not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type .{file_ext} not supported. Only PDF and DOCX files are allowed."
                )
        
        count = await ingest_files(files, user_id, document_id)
        
        return IngestResponse(
            message="Documents ingested successfully",
            documents_count=count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
