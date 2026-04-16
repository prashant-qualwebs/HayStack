from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.ingestion import IngestResponse
from app.services.ingestion_service import ingest_file
from app.core.exceptions import ValidationError, ProcessingError

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(file: UploadFile = File(...), user_id: str = Form("default_user")):
    if not user_id or not user_id.strip():
        user_id = "default_user"
    
    if not file:
        raise ValidationError("No file provided")
    
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise ValidationError("Only PDF and DOCX files are allowed")
    
    try:
        content = await file.read()
        count = await ingest_file(content, file.filename, user_id)
        return IngestResponse(message=f"File '{file.filename}' ingested successfully", documents_count=count, user_id=user_id)
    except Exception as e:
        raise ProcessingError(f"Ingestion failed: {str(e)}")
