from typing import List

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

from app.haystack.document_store.elastic import document_store
from app.haystack.processors.embedding import document_embedder
from app.schemas.ingestion import IngestChunk


def ingest_chunks(chunks: List[IngestChunk]) -> int:
    documents = [
        Document(
            content=chunk.text.strip(),
            meta={
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
            },
        )
        for chunk in chunks
    ]

    if not documents:
        return 0

    embedded_documents = document_embedder.run(documents=documents)["documents"]
    return document_store.write_documents(
        embedded_documents,
        policy=DuplicatePolicy.OVERWRITE,
    )
