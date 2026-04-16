from typing import Dict
from app.haystack.pipelines.hybrid_rag_pipeline import get_hybrid_rag_pipeline


def retrieve_and_generate_hybrid(query: str, user_id: str, top_k: int = None, retrieval_top_k: int = None) -> Dict:
    user_filter = {"field": "user_id", "operator": "==", "value": user_id}
    hybrid_pipeline = get_hybrid_rag_pipeline(top_k=top_k, retrieval_top_k=retrieval_top_k)
    
    result = hybrid_pipeline.run({
        "text_embedder": {"text": query},
        "dense_retriever": {"filters": user_filter},
        "bm25_retriever": {"query": query, "filters": user_filter},
        "ranker": {"query": query},
        "prompt_builder": {"query": query}
    })
    
    documents = result["ranker"]["documents"]
    answer = result["llm"]["replies"][0]
    
    return {
        "query": query,
        "answer": answer,
        "retrieved_documents": [
            {"content": doc.content, "score": doc.score, "metadata": doc.meta}
            for doc in documents
        ]
    }
