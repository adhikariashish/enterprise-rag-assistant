from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from app.rag.ingest.loader_pdf import load_pdf
from app.rag.ingest.chunker import chunk_text

from app.rag.store.chroma_store import ChromaStore
from app.rag.embeddings.embedder_base import Embedder

@dataclass
class IngestPipelineConfig:
    docs_root: Path = Path("data") / "docs"
    allowed_ext: tuple[str, ...] = (".pdf",)

    # chunking params
    chunk_size: int = 1000
    chunk_overlap: int = 200


def inter_pdf_files(docs_root: Path) -> Iterable[tuple[str, Path]]:
    """
    Iterate PDF files in the given directory.
    Yields tuples of (relative_path_str, full_path).
    """
    for doc_type_dir in sorted([p for p in docs_root.iterdir() if p.is_dir()]):
        doc_type = doc_type_dir.name.lower()
        for fp in sorted(doc_type_dir.glob("*.pdf")):
            yield (doc_type, fp)

def ingest_folder(cfg: IngestPipelineConfig, *, embedder: Embedder, store: ChromaStore) -> int:
    """
    Ingest documents from the specified folder into the vector store.
    returns the total number of chunks ingested/added.
    """
    if not cfg.docs_root.exists():
        raise FileNotFoundError(f"Docs root not found: {cfg.docs_root.resolve()}")

    total_chunks = 0

    for doc_type, pdf_path in inter_pdf_files(cfg.docs_root):
        pages = load_pdf(pdf_path)
        print(f"[{doc_type}] {pdf_path.name} : pages = {len(pages)}")

        for page in pages:
            chunks = chunk_text(page.text, chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)
            if not chunks:
                continue

            # get ids and metadatas for each chunk
            ids = [f"{pdf_path.name}::p{page.page}::c{idx}" for idx in range(len(chunks))]
            metadatas = [
                {
                    "source": pdf_path.name,
                    "doc_type": doc_type,
                    "page": page.page,
                }
                for _ in chunks
            ]

            # embed
            vecs = embedder.embed_many(chunks)
            # upsert
            store.upsert(
                ids=ids,
                documents=chunks,
                embeddings=vecs,
                metadatas=metadatas,
            )

            total_chunks += len(chunks)

    return total_chunks
    