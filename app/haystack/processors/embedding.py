from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from app.core.config import settings


def get_document_embedder():
    return SentenceTransformersDocumentEmbedder(model=settings.EMBEDDING_MODEL, progress_bar=True)


def get_text_embedder():
    return SentenceTransformersTextEmbedder(model=settings.EMBEDDING_MODEL)


document_embedder = get_document_embedder()
text_embedder = get_text_embedder()
