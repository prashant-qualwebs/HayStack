from typing import List

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

from app.core.config import settings
from app.haystack.document_store.elastic import document_store
from app.haystack.processors.embedding import document_embedder
from app.schemas.ingestion import IngestChunk


def _indexing_window() -> int:
    return max(0, settings.INDEXING_CONTEXT_WINDOW)


def _document_id_filter(document_id: str) -> dict:
    return {
        "field": "meta.document_id",
        "operator": "==",
        "value": document_id,
    }


def _delete_existing_documents(document_ids: set[str]) -> None:
    existing_document_ids = []
    for document_id in document_ids:
        existing_documents = document_store.filter_documents(
            filters=_document_id_filter(document_id)
        )
        existing_document_ids.extend(document.id for document in existing_documents)

    if existing_document_ids:
        document_store.delete_documents(existing_document_ids)


def _chunk_metadata(chunk: IngestChunk) -> dict:
    return {
        "document_id": chunk.document_id,
        "chunk_id": chunk.chunk_id,
        "chunk_index": chunk.chunk_index,
    }


def _create_window_documents(chunks: List[IngestChunk]) -> List[Document]:
    window = _indexing_window()
    chunks_by_document_id = {}
    for chunk in chunks:
        chunks_by_document_id.setdefault(chunk.document_id, []).append(chunk)

    documents = []
    for document_id, document_chunks in chunks_by_document_id.items():
        sorted_chunks = sorted(document_chunks, key=lambda chunk: chunk.chunk_index)

        for position, chunk in enumerate(sorted_chunks):
            start = max(0, position - window)
            end = min(len(sorted_chunks), position + window + 1)
            window_chunks = sorted_chunks[start:end]

            documents.append(
                Document(
                    id=f"{document_id}:{chunk.chunk_id}:{chunk.chunk_index}:w{window}",
                    content="\n\n".join(
                        source_chunk.text.strip()
                        for source_chunk in window_chunks
                        if source_chunk.text.strip()
                    ),
                    meta={
                        "document_id": document_id,
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "indexing_context_window": window,
                        "matched_chunk": {
                            "metadata": _chunk_metadata(chunk),
                        },
                        "source_chunks": [
                            {
                                "content": source_chunk.text.strip(),
                                "metadata": _chunk_metadata(source_chunk),
                            }
                            for source_chunk in window_chunks
                        ],
                    },
                )
            )

    return documents


def ingest_chunks(chunks: List[IngestChunk]) -> int:
    documents = _create_window_documents(chunks)

    if not documents:
        return 0

    _delete_existing_documents({chunk.document_id for chunk in chunks})

    embedded_documents = document_embedder.run(documents=documents)["documents"]
    return document_store.write_documents(
        embedded_documents,
        policy=DuplicatePolicy.OVERWRITE,
    )
