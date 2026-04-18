from haystack.components.preprocessors import DocumentSplitter
from app.core.config import settings


def get_document_splitter():
    return DocumentSplitter(
        split_by=settings.SPLIT_BY, 
        split_length=settings.CHUNK_SIZE, 
        split_overlap=settings.CHUNK_OVERLAP
    )
