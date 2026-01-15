from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class QueryRouterConfig:
    # doc_type values from metadata
    moa_key: str = "moa"
    aoa_key: str = "aoa"
    memo_key: str = "memo"
    rule_key: str = "rule"


class QueryRouter:
    """
        keyword-based router that returns a Chroma 'where' filter.
    """

    def __init__(self, cfg: QueryRouterConfig | None = None) -> None:
        self.cfg = cfg or QueryRouterConfig()

    def route_where(self, question: str) -> Optional[Dict[str, Any]]:
        q = (question or "").lower()

        if "moa" in q:
            return {"doc_type": self.cfg.moa_key}
        if "aoa" in q:
            return {"doc_type": self.cfg.aoa_key}
        if "memo" in q or "memos" in q:
            return {"doc_type": self.cfg.memo_key}
        if "rule" in q or "rules" in q or "policy" in q:
            return {"doc_type": self.cfg.rule_key}

        return None
