from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from app.core.config import settings


def get_document_store():
    return ElasticsearchDocumentStore(hosts=settings.ELASTICSEARCH_HOST, index=settings.ELASTICSEARCH_INDEX)


document_store = get_document_store()
