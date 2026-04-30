from typing import Dict, List

from haystack import Document

from app.core.config import settings
from app.haystack.pipelines.hybrid_rag_pipeline import hybrid_rag_pipeline


def _top_k() -> int:
    return max(1, settings.DEFAULT_QUERY_TOP_K)


def _format_response(query: str, documents: List[Document]) -> Dict:
    return {
        "query": query,
        "retrieved_documents": [
            {"content": doc.content, "score": doc.score, "metadata": doc.meta}
            for doc in documents
        ],
    }


def _metadata_filter(field: str, value: str) -> Dict:
    return {
        "field": f"meta.{field}",
        "operator": "==",
        "value": value,
    }


def _retrieval_filters(document_id: str | None, user_id: str) -> Dict:
    conditions = []
    if document_id:
        conditions.append(_metadata_filter("document_id", document_id))
    conditions.append(_metadata_filter("user_id", user_id))

    if len(conditions) == 1:
        return conditions[0]

    return {"operator": "AND", "conditions": conditions}


def _passes_min_score(document: Document) -> bool:
    return document.score is None or document.score >= settings.MIN_RETRIEVAL_SCORE


def _source_chunk_key(source_chunk: Dict) -> tuple:
    metadata = source_chunk.get("metadata", {})
    return (
        metadata.get("document_id"),
        metadata.get("user_id"),
        metadata.get("tag"),
        metadata.get("order"),
    )


def _rank_source_chunks(query: str, document: Document) -> Document | None:
    source_chunks = document.meta.get("source_chunks")
    if not source_chunks:
        return document

    source_documents = [
        Document(
            content=source_chunk.get("content", ""),
            meta=source_chunk.get("metadata", {}),
        )
        for source_chunk in source_chunks
        if source_chunk.get("content")
    ]
    if not source_documents:
        return None

    ranker = hybrid_rag_pipeline.get_component("ranker")
    result = ranker.run(
        query=query,
        documents=source_documents,
        top_k=len(source_documents),
    )

    ranked_source_documents = [
        source_document
        for source_document in result["documents"]
        if source_document.score is not None
        and source_document.score >= settings.SOURCE_CHUNK_SCORE_THRESHOLD
    ]
    if not ranked_source_documents:
        return None

    ranked_source_documents = sorted(
        ranked_source_documents,
        key=lambda source_document: source_document.meta.get("order", 0),
    )

    return Document(
        content="\n\n".join(
            source_document.content
            for source_document in ranked_source_documents
            if source_document.content
        ),
        score=document.score,
        meta={
            **document.meta,
            "source_chunks": [
                {
                    "content": source_document.content,
                    "score": source_document.score,
                    "metadata": source_document.meta,
                }
                for source_document in ranked_source_documents
            ],
        },
    )


def _filter_and_dedupe_documents(query: str, documents: List[Document]) -> List[Document]:
    filtered_documents = []
    seen_source_chunks = set()

    for document in documents:
        if not _passes_min_score(document):
            continue

        filtered_document = _rank_source_chunks(query, document)
        if filtered_document is None:
            continue

        source_chunks = filtered_document.meta.get("source_chunks", [])
        source_keys = tuple(_source_chunk_key(source_chunk) for source_chunk in source_chunks)
        if source_keys and source_keys in seen_source_chunks:
            continue

        seen_source_chunks.add(source_keys)
        filtered_documents.append(filtered_document)

    return filtered_documents


def retrieve_and_generate(
    query: str,
    user_id: str,
    document_id: str | None = None,
) -> Dict:
    top_k = _top_k()
    document_id = document_id.strip() if document_id else None
    user_id = user_id.strip()
    filters = _retrieval_filters(document_id, user_id)

    pipeline_input = {
        "text_embedder": {"text": query},
        "bm25_retriever": {
            "query": query,
            "top_k": settings.BM25_RETRIEVER_TOP_K,
            "filters": filters,
        },
        "dense_retriever": {
            "top_k": settings.DENSE_RETRIEVER_TOP_K,
            "filters": filters,
        },
        "ranker": {"query": query, "top_k": top_k},
    }

    result = hybrid_rag_pipeline.run(pipeline_input)
    documents = _filter_and_dedupe_documents(query, result["ranker"]["documents"])
    return _format_response(query, documents)
