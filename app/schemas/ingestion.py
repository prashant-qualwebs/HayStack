from pydantic import BaseModel


class IngestRequest(BaseModel):
    user_id: str


class IngestResponse(BaseModel):
    message: str
    documents_count: int
    user_id: str
