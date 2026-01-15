from pathlib import Path
from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig

if __name__ == "__main__":
    # Simple smoke test to verify ChromaStore can be initialized
    cfg = ChromaStoreConfig(
        persist_directory=Path("storage")/ "vectordb",
        collection_name="consultancy_kb",        
    )
    
    store = ChromaStore(cfg)
    heartbeat = store.heartbeat()
    print(f"ChromaStore Heartbeat: {heartbeat}")