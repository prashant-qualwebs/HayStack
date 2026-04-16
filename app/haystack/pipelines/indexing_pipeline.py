from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from app.haystack.processors.splitter import get_document_splitter
from app.haystack.processors.embedding import document_embedder
from app.haystack.document_store.elastic import document_store


def create_indexing_pipeline():
    pipeline = Pipeline()
    pipeline.add_component("splitter", get_document_splitter())
    pipeline.add_component("embedder", document_embedder)
    pipeline.add_component("writer", DocumentWriter(document_store=document_store, policy="upsert"))
    pipeline.connect("splitter.documents", "embedder.documents")
    pipeline.connect("embedder.documents", "writer.documents")
    return pipeline


indexing_pipeline = create_indexing_pipeline()
