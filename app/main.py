from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import setup_middleware
from app.api.v1.router import api_router

app = FastAPI()

setup_middleware(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "RAG API is running", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
