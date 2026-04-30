from typing import List

from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

from app.core.config import settings
from app.haystack.document_store.elastic import document_store
from app.haystack.processors.embedding import document_embedder
from app.schemas.ingestion import IngestChunk


def _indexing_window() -> int:
    return max(0, settings.INDEXING_CONTEXT_WINDOW)


def _metadata_filter(field: str, value: str) -> dict:
    return {
        "field": f"meta.{field}",
        "operator": "==",
        "value": value,
    }


def _document_user_filter(document_id: str, user_id: str) -> dict:
    return {
        "operator": "AND",
        "conditions": [
            _metadata_filter("document_id", document_id),
            _metadata_filter("user_id", user_id),
        ],
    }


def _delete_existing_documents(document_users: set[tuple[str, str]]) -> None:
    existing_document_ids = []
    for document_id, user_id in document_users:
        existing_documents = document_store.filter_documents(
            filters=_document_user_filter(document_id, user_id)
        )
        existing_document_ids.extend(document.id for document in existing_documents)

    if existing_document_ids:
        document_store.delete_documents(existing_document_ids)


def _chunk_tag(chunk: IngestChunk) -> str:
    return chunk.tag.strip() if chunk.tag and chunk.tag.strip() else f"auto_chunk_{chunk.order}"


def _chunk_metadata(chunk: IngestChunk) -> dict:
    return {
        "document_id": chunk.document_id,
        "user_id": chunk.user_id,
        "tag": _chunk_tag(chunk),
        "order": chunk.order,
    }


def _create_window_documents(chunks: List[IngestChunk]) -> List[Document]:
    window = _indexing_window()
    chunks_by_document_user = {}
    for chunk in chunks:
        key = (chunk.document_id, chunk.user_id)
        chunks_by_document_user.setdefault(key, []).append(chunk)

    documents = []
    for (document_id, user_id), document_chunks in chunks_by_document_user.items():
        sorted_chunks = sorted(document_chunks, key=lambda chunk: chunk.order)

        for chunk in sorted_chunks:
            start_index = chunk.order - window
            end_index = chunk.order + window
            window_chunks = [
                source_chunk
                for source_chunk in sorted_chunks
                if start_index <= source_chunk.order <= end_index
            ]

            documents.append(
                Document(
                    id=f"{document_id}:{chunk.user_id}:{_chunk_tag(chunk)}:{chunk.order}:w{window}",
                    content="\n\n".join(
                        source_chunk.text.strip()
                        for source_chunk in window_chunks
                        if source_chunk.text.strip()
                    ),
                    meta={
                        "document_id": document_id,
                        "user_id": chunk.user_id,
                        "tag": _chunk_tag(chunk),
                        "order": chunk.order,
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

    _delete_existing_documents({(chunk.document_id, chunk.user_id) for chunk in chunks})

    embedded_documents = document_embedder.run(documents=documents)["documents"]
    return document_store.write_documents(
        embedded_documents,
        policy=DuplicatePolicy.OVERWRITE,
    )
