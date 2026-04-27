from typing import Dict, List

from haystack import Document

from app.core.config import settings
from app.haystack.document_store.elastic import document_store
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


def _documents_for_document_id(document_id: str) -> List[Document]:
    documents = document_store.filter_documents()
    return [
        document
        for document in documents
        if document.meta.get("document_id") == document_id
    ]


def retrieve_and_generate(
    query: str,
    document_id: str | None = None,
) -> Dict:
    top_k = _top_k()
    document_id = document_id.strip() if document_id else None

    if document_id:
        documents = _documents_for_document_id(document_id)
        if not documents:
            return _format_response(query, [])

        ranker = hybrid_rag_pipeline.get_component("ranker")
        result = ranker.run(query=query, documents=documents, top_k=top_k)
        return _format_response(query, result["documents"])

    pipeline_input = {
        "text_embedder": {"text": query},
        "bm25_retriever": {"query": query, "top_k": top_k},
        "dense_retriever": {"top_k": top_k},
        "ranker": {"query": query, "top_k": top_k},
    }

    result = hybrid_rag_pipeline.run(pipeline_input)
    return _format_response(query, result["ranker"]["documents"])
