from __future__ import annotations
from typing import List
from dataclasses import dataclass

@dataclass(frozen=True)
class ContextPackerConfig:
    max_context_chars: int
    max_chunks_in_prompt:int


class ContextPacker:
    """
        Packs retrieved docs into a single context string with:
            - chunk/chars limits
            - duplicate removal
    """

    def __init__(self, cfg: ContextPackerConfig) -> None:
        self.cfg = cfg
    
    def pack(self, docs: List[str]) -> str:

        packed: List[str] = []
        seen_norm: set[str] = set()
        total = 0

        for doc in docs:
            doc = (doc or "").strip()
            if not doc:
                continue

            # simple normalization to avoid duplicates
            norm = " ".join(doc.lower().split())
            if norm in seen_norm:
                continue
            seen_norm.add(norm)

            # enforce max chars limit
            if len(packed) >= self.cfg.max_chunks_in_prompt:
                break

            # enforce total char limit
            remaining = self.cfg.max_context_chars - total
            if remaining <= 0:
                break

            # trim doc if needed
            snippet = doc if len(doc) <= remaining else (doc[: max(0, remaining - 3)] + "...")
            packed.append(snippet)
            total += len(snippet)
            
        return "\n\n---\n\n".join(packed).strip()
