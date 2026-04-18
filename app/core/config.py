from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API"
    
    # Elasticsearch Settings
    ELASTICSEARCH_HOST: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "documents"
    
    # Embedding Model Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    
    # Ranker Settings
    RANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # Retrieval Settings
    DENSE_RETRIEVER_TOP_K: int = 10
    BM25_RETRIEVER_TOP_K: int = 10
    RANKER_TOP_K: int = 5
    DEFAULT_QUERY_TOP_K: int = 5
    
    # Document Splitting Settings
    SPLIT_BY: str = "word"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
