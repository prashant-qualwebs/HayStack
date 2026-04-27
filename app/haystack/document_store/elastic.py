from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from app.core.config import settings


def get_document_store():
    kwargs = {
        "hosts": settings.ELASTICSEARCH_HOST,
        "index": settings.ELASTICSEARCH_INDEX,
    }

    if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
        kwargs["basic_auth"] = (
            settings.ELASTICSEARCH_USERNAME,
            settings.ELASTICSEARCH_PASSWORD,
        )

    return ElasticsearchDocumentStore(**kwargs)


document_store = get_document_store()
