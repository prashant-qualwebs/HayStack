from typing import Dict
from app.haystack.pipelines.hybrid_rag_pipeline import hybrid_rag_pipeline


def retrieve_and_generate(query: str, user_id: str, top_k: int = 5) -> Dict:
    filters = {
        "operator": "AND",
        "conditions": [
            {"field": "meta.user_id", "operator": "==", "value": user_id}
        ]
    }
    
    result = hybrid_rag_pipeline.run({
        "text_embedder": {"text": query},
        "bm25_retriever": {"query": query, "filters": filters, "top_k": top_k},
        "dense_retriever": {"filters": filters, "top_k": top_k},
        "ranker": {"query": query, "top_k": top_k}
    })
    
    documents = result["ranker"]["documents"]
    
    return {
        "query": query,
        "retrieved_documents": [
            {"content": doc.content, "score": doc.score}
            for doc in documents
        ]
    }
