from pathlib import Path

from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig
from app.rag.embeddings.embedder_base import Embedder
from app.rag.embeddings.ollama_embedder import OllamaEmbedder, OllamaEmbedderConfig

def pretty_print(results: dict) -> None:
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    print("\n=== Top Results ===")
    print("=========================")
    for rank, (i, d, m, dist) in enumerate(zip(ids, docs, metas, dists), start=1):
        print(f"\n--- Rank {rank} ---")
        print(f"ID: {i}")
        print(f"Distance: {dist}")
        print(f"Metadata: {m}")
        print(f"Text: {d}")

if __name__ == "__main__":
    # 1) Load store
    store = ChromaStore(
        ChromaStoreConfig(
            persist_directory=Path("storage") / "vectordb",
            collection_name="consultancy_kb",
        )
    )

    # 2) Build embedder
    embedder: Embedder = OllamaEmbedder(OllamaEmbedderConfig(model="nomic-embed-text"))

    # 3) Ask a query
    question = "What is the deadline for reimbursements?"
    q_vec = embedder.embed_one(question)

    # 4) Retrieve
    results = store.query(query_embeddings=[q_vec], n_results=3)

    # 5) Print
    pretty_print(results)