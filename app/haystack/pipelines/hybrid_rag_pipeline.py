from haystack import Pipeline
from haystack.components.joiners import DocumentJoiner
from app.haystack.processors.embedding import text_embedder
from app.haystack.retrievers.dense import get_retriever as get_dense_retriever
from app.haystack.retrievers.bm25 import get_bm25_retriever
from app.haystack.rankers.cross_encoder import get_ranker
from app.core.config import settings


def create_hybrid_rag_pipeline():
    pipeline = Pipeline()
    
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("dense_retriever", get_dense_retriever(top_k=settings.DENSE_RETRIEVER_TOP_K))
    pipeline.add_component("bm25_retriever", get_bm25_retriever(top_k=settings.BM25_RETRIEVER_TOP_K))
    pipeline.add_component("document_joiner", DocumentJoiner())
    pipeline.add_component("ranker", get_ranker(top_k=settings.RANKER_TOP_K))
    
    pipeline.connect("text_embedder.embedding", "dense_retriever.query_embedding")
    pipeline.connect("dense_retriever.documents", "document_joiner.documents")
    pipeline.connect("bm25_retriever.documents", "document_joiner.documents")
    pipeline.connect("document_joiner.documents", "ranker.documents")
    
    return pipeline


hybrid_rag_pipeline = create_hybrid_rag_pipeline()
