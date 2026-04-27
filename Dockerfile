FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV API_V1_STR=/api/v1
ENV PROJECT_NAME="RAG API"
ENV ELASTICSEARCH_HOST=http://localhost:9200
ENV ELASTICSEARCH_INDEX=documents
ENV EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ENV EMBEDDING_DIM=384
ENV RETRIEVAL_TOP_K=20
ENV RERANK_TOP_K=5
ENV SPLITTER_SPLIT_BY=word
ENV SPLITTER_SPLIT_LENGTH=512
ENV SPLITTER_SPLIT_OVERLAP=32
ENV RANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
ENV DEFAULT_USER_ID=default_user

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
