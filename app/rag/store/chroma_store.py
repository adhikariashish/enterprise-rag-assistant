from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings


@dataclass
class ChromaStoreConfig:
    persist_directory: Path
    collection_name: str = "consultancy_kb"

class ChromaStore:
    """
    Block 5: Vector Store (Chroma)

    For Step 1.1 we only:
      - create/load a persistent Chroma client
      - create/load a collection

    Later steps will add:
      - upsert (vectors + documents + metadata) - done here
      - query (similarity search)
    """

    def __init__(self, cfg: ChromaStoreConfig):
        self.cfg = cfg
        self.cfg.persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(self.cfg.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.cfg.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def collection_name(self) -> str:
        return self._collection.name

    def heartbeat(self) -> Dict[str, Any]:
        """
        Quick sanity check:
        - returns what collection we loaded
        - and how many items exist (will be 0 for now)
        """
        count = self._collection.count()
        return {"collection": self._collection.name, "count": count}

    def upsert(
        self,
        *,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Store vectors + text + metadata in Chroma.
        """
        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
    
    def query(
        self,
        *,
        query_embeddings: List[List[float]],
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Similarity search in Chroma.
        Returns documents + metadatas + distances.
        """
        return self._collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )