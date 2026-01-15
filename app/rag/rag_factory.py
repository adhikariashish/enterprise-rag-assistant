from pathlib import Path
from app.core.config import get_settings
from app.rag.rag_service import RAGService
from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig

def create_rag_service(embedder, llm) -> RAGService:
    settings = get_settings()

    store = ChromaStore(
        ChromaStoreConfig(
            collection_name=settings.rag.collection_name,
            persist_directory=Path(settings.rag.persist_dir),
        )
    )

    return RAGService(
        embedder=embedder,
        llm=llm,
        store=store,
    )