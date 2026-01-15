import math
import re
from dataclasses import dataclass
from typing import Any, List


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# If the user message looks like a real question, NEVER treat it as "closing"
QUESTION_CUES = re.compile(
    r"(\?)|^(who|what|when|where|why|how|can|could|would|should|do|does|did|is|are|am|will|may)\b",
    re.IGNORECASE
)

# Only treat as closing when user explicitly signals they are done
CLOSE_PHRASES = re.compile(
    r"\b(thanks|thank you|thx|bye|goodbye|that's all|thats all|done|all good|no more|nothing else|bie|bye|no worries)\b",
    re.IGNORECASE
)


def _avg(vectors: List[List[float]]) -> List[float]:
    n = len(vectors)
    if n == 0:
        return []
    dim = len(vectors[0])
    return [sum(v[i] for v in vectors) / n for i in range(dim)]


@dataclass
class IntentRouter:
    embedder: Any
    q_anchor: List[float]
    close_anchor: List[float]

    @classmethod
    def build(cls, embedder: Any) -> "IntentRouter":
        # Better anchors (multi-example) — reduces random misfires
        q_texts = [
            "User asks a question about the documents.",
            "User wants an answer or explanation.",
            "User asks for clarification or a follow-up."
        ]
        close_texts = [
            "User says thank you.",
            "User says goodbye.",
            "User is done and ends the conversation."
        ]

        q_anchor = _avg([embedder.embed_one(t) for t in q_texts])
        close_anchor = _avg([embedder.embed_one(t) for t in close_texts])

        return cls(embedder=embedder, q_anchor=q_anchor, close_anchor=close_anchor)

    def is_closing(self, text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return True

        # 1) Hard guard: if it looks like a question, don't close
        if QUESTION_CUES.search(t):
            return False

        # 2) Hard guard: only close on explicit closing phrases
        # (This prevents “ok but …” / “im asking …” from being treated as closing)
        if not CLOSE_PHRASES.search(t):
            return False

        # 3) Optional: embedding confirmation with threshold + margin
        v = self.embedder.embed_one(t)
        sim_close = _cosine(v, self.close_anchor)
        sim_q = _cosine(v, self.q_anchor)

        # Require BOTH a minimum similarity and a margin
        return (sim_close > 0.35) and ((sim_close - sim_q) > 0.05)
