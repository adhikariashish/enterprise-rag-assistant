# app/rag/container.py
from functools import lru_cache
from app.rag.providers_factory import create_providers
from app.rag.rag_factory import create_rag_service

@lru_cache(maxsize=1)
def get_rag():
    embedder, llm = create_providers()
    return create_rag_service(embedder, llm)
