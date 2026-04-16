from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.joiners import DocumentJoiner
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.utils import Secret
from app.haystack.retrievers.dense import get_retriever as get_dense_retriever
from app.haystack.retrievers.bm25 import get_bm25_retriever
from app.haystack.rankers.cross_encoder import get_ranker
from app.core.config import settings


PROMPT_TEMPLATE = """Answer the following question based on the provided context documents.
If the answer cannot be found in the context, say "I don't have enough information to answer this question."

Context:
{% for doc in documents %}
Document {{ loop.index }}:
{{ doc.content }}

{% endfor %}

Question: {{ query }}

Answer:
"""


def create_hybrid_rag_pipeline(top_k: int = 5, retrieval_top_k: int = 20):
    pipeline = Pipeline()
    
    text_embedder = SentenceTransformersTextEmbedder(model=settings.EMBEDDING_MODEL)
    dense_retriever = get_dense_retriever(top_k=retrieval_top_k)
    bm25_retriever = get_bm25_retriever(top_k=retrieval_top_k)
    document_joiner = DocumentJoiner()
    ranker = get_ranker(top_k=top_k)
    
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("dense_retriever", dense_retriever)
    pipeline.add_component("bm25_retriever", bm25_retriever)
    pipeline.add_component("document_joiner", document_joiner)
    pipeline.add_component("ranker", ranker)
    pipeline.add_component("prompt_builder", PromptBuilder(template=PROMPT_TEMPLATE))
    pipeline.add_component("llm", OpenAIGenerator(
        api_key=Secret.from_token(settings.OPENAI_API_KEY),
        model=settings.OPENAI_MODEL,
        generation_kwargs={"temperature": 0.2, "max_tokens": 2000}
    ))
    
    pipeline.connect("text_embedder.embedding", "dense_retriever.query_embedding")
    pipeline.connect("dense_retriever.documents", "document_joiner.documents")
    pipeline.connect("bm25_retriever.documents", "document_joiner.documents")
    pipeline.connect("document_joiner.documents", "ranker.documents")
    pipeline.connect("ranker.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder.prompt", "llm.prompt")
    
    return pipeline


def get_hybrid_rag_pipeline(top_k: int = 5, retrieval_top_k: int = 20):
    return create_hybrid_rag_pipeline(top_k=top_k, retrieval_top_k=retrieval_top_k)
