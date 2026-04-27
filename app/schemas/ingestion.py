from pydantic import BaseModel


class IngestChunk(BaseModel):
    document_id: str
    chunk_id: int
    chunk_index: int
    text: str


class IngestResponse(BaseModel):
    message: str
    documents_count: int
