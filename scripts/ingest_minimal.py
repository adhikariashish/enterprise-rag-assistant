from pathlib import Path
from uuid import uuid4

from app.rag.store.chroma_store import ChromaStore, ChromaStoreConfig
from app.rag.embeddings.embedder_base import Embedder
from app.rag.embeddings.ollama_embedder import OllamaEmbedder, OllamaEmbedderConfig

def simple_chunk(text: str, max_chars: int = 350) -> list[str]:
    # MVP chunker: split by lines, then pack into <= max_chars blocks
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    chunks: list[str] = []
    buff = ""
    for ln in lines:
        if len(buff) + len(ln) + 1 <= max_chars:
            buff = (buff + " " + ln).strip()
        else:
            chunks.append(buff)
            buff = ln
    if buff:
        chunks.append(buff)
    return chunks


if __name__ == "__main__":
    # 1) Load sample text
    p = Path("data") / "samples" / "sample_policy.txt"
    text = p.read_text(encoding="utf-8")

    # 2) Chunk
    chunks = simple_chunk(text)
    print(f"Chunks: {len(chunks)}")

    # 3) Embed (typed as base interface)
    embedder: Embedder = OllamaEmbedder(
        OllamaEmbedderConfig(model="nomic-embed-text")
    )
    vectors = embedder.embed_many(chunks)
    print(f"Embedded: {len(vectors)} | dim={len(vectors[0])}")

    # 4) Upsert into Chroma
    store = ChromaStore(
        ChromaStoreConfig(persist_directory=Path("storage") / "vectordb")
    )
    ids = [str(uuid4()) for _ in chunks]
    metadatas = [{"source": p.name, "doc_type": "moa"} for _ in chunks]

    store.upsert(ids=ids, documents=chunks, embeddings=vectors, metadatas=metadatas)

    # 5) Verify count
    print("ChromaStore Heartbeat:", store.heartbeat())