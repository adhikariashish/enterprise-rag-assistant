from __future__ import annotations
from pathlib import Path

from app.rag.ingest.pipeline import IngestPipelineConfig, ingest_folder
from app.rag.embeddings.ollama_embedder import OllamaEmbedder, OllamaEmbedderConfig
from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig

from app.core.config import get_settings

def main():

    settings = get_settings()
    
    # embedder
    embedder = OllamaEmbedder(
        OllamaEmbedderConfig(model_name=settings.ollama.embeddings.model_name))
    
    # vector store
    store = ChromaStore(
        ChromaStoreConfig(persist_directory=Path("storage") / "vectordb", collection_name=settings.rag.collection_name)
        )

    # ingest pipeline config
    ingest_cfg = IngestPipelineConfig(
        docs_root=Path("data") / "docs",
        allowed_ext=(".pdf",),
        chunk_size=1000,
        chunk_overlap=200,
    )

    total_chunks = ingest_folder(
        ingest_cfg, embedder=embedder, store=store)
    
    print(f"Total chunks ingested: {total_chunks}")

if __name__ == "__main__":
    main()
