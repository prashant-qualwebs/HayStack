from haystack.components.preprocessors import DocumentSplitter
from app.core.config import settings


def get_document_splitter(split_by: str = None, split_length: int = None, split_overlap: int = None):
    return DocumentSplitter(
        split_by=split_by or settings.SPLITTER_SPLIT_BY,
        split_length=split_length or settings.SPLITTER_SPLIT_LENGTH,
        split_overlap=split_overlap or settings.SPLITTER_SPLIT_OVERLAP
    )
