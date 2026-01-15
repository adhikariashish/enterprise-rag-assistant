from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

from app.api.schemas import Citation

@dataclass(frozen=True)
class RetrieverConfig:
    top_k: int
    retrieval_pool_k: int


class Retriever:
    """
        Retrieve top-k relevant documents for the given question.

        Returns:
            A tuple containing:
            - List of retrieved document texts
            - List of corresponding citations

    """

    def __init__(self, *, embedder, store:Any, cfg: RetrieverConfig)-> None:
        self.embedder=embedder
        self.store= store
        self.cfg = cfg or RetrieverConfig()

    
    def retrieve(self, question:str, *, where: Optional[Dict[str, Any]] = None) -> Tuple[List[str], List[Citation], List[float]]:

        q_vec = self.embedder.embed_one(question)
        pool_k = max(self.cfg.retrieval_pool_k, self.cfg.top_k)

        results = self.store.query(
            query_embeddings=[q_vec], 
            n_results=pool_k, 
            where=where,
        )

        # print("DEBUG: RAGService.retrieve results:", results.keys())
        # print("DEBUG: RAGService.retrieve results[ids]:", results.get("ids", [[]]))
        # print("DEBUG: RAGService.retrieve results[distances]:", results.get("distances", [[]])[0][:3])
        # print("DEBUG: RAGService.retrieve results[metadatas]:", results.get("metadatas", [[]])[0][:3])

        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        if not ids:
            return [],[],[]

        # rerank locally by distanct (smaller distance = more similar)
        items = list(zip(ids, docs, metas, dists))
        items.sort(key=lambda x: x[3] if x[3] is not None else float("inf"))

        top_k = self.cfg.top_k
        picked = []
        seen = set()

        for cid, doc, meta, dist in items:
            source = str((meta or {}).get("source", "unknown"))
            page = (meta or {}).get("page", None)
            key = (source, page)

            if key in seen:
                continue
            
            picked.append((cid, doc, meta, dist))
            seen.add(key)

            if len(picked) >= top_k:
                break
        
        if len(picked) < top_k:
            for cid, doc, meta, dist in items:
                if (cid, doc, meta, dist) in picked:
                    continue
                picked.append((cid, doc, meta, dist))
                if len(picked) >= top_k:
                    break
        
        # overwrite arrays with the selected set
        ids = [p[0] for p in picked] 
        docs = [p[1] for p in picked] 
        metas = [p[2] for p in picked] 
        dists = [p[3] for p in picked] 

        citations: List[Citation] = []
        for cid, doc, meta, dist in zip(ids, docs, metas, dists):
            # metadata may be None if not stored, so be safe
            meta = meta or {}
            source = str(meta.get("source", "unknown"))
            doc_type_val = meta.get("doc_type", None)
            page_val = meta.get("page", None)

            # conversions
            doc_type = str(doc_type_val) if doc_type_val is not None else None
            try:
                page = int(page_val) if page_val is not None else None
            except (TypeError, ValueError):
                page = None

            snippet = (doc or "").replace("\n", " ").strip()
            snippet = snippet[:160] + "..." if len(snippet) > 160 else snippet

            citations.append(
                Citation(
                    source=source,
                    doc_type=doc_type,
                    page=page,
                    chunk_id=str(cid),
                    snippet=snippet if snippet else None,
                )
            )

        return docs, citations, dists