from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API"
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 2000
    ELASTICSEARCH_HOST: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "documents"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 5
    SPLITTER_SPLIT_BY: str = "word"
    SPLITTER_SPLIT_LENGTH: int = 512
    SPLITTER_SPLIT_OVERLAP: int = 32
    RANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    DEFAULT_USER_ID: str = "default_user"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
