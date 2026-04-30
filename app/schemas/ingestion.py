from pydantic import BaseModel


class IngestChunk(BaseModel):
    document_id: str
    user_id: str
    tag: str | None = None
    order: int
    text: str | None = None


class IngestResponse(BaseModel):
    message: str
    documents_count: int
