from pydantic import BaseModel


class IngestResponse(BaseModel):
    message: str
    documents_count: int
