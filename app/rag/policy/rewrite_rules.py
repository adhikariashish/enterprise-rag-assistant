# app/rag/policy/rewrite_rules.py
from __future__ import annotations
import re

_VAGUE_PATTERNS = [
    r"\bwhat about\b",
    r"\btell me about\b",
    r"\bcan you explain\b",
    r"\bcan you clarify\b",
    r"\bwhat does(it|this|that) mean\b",
    r"\bclarification\b",
    r"\bdoes that\b",
    r"\bdo they\b",
    r"\bexplain that\b",
    r"\bexpand on\b",
    r"\bwhy\b",
    r"\bhow about\b",
    r"\band\bs*$",
    r"\btell me more\b",
]

_EXPLICIT_TOKENS = ["moa", "aoa", "memo", "rule", "rules", "policy"]
_PRONOUNS = ["it", "this", "that", "they", "them", "he", "she", "his", "her", "its"]

def should_rewrite(question: str, max_words: int) -> bool:
    q = (question or "").strip().lower()
    if not q:
        return False

    # short: likely missing context
    if len(q.split()) <= max_words:
        # don't rewrite short queries that already specify doc type
        if any(tok in q for tok in _EXPLICIT_TOKENS):
            return False
        return True

    # vague patterns
    if any(re.search(pat, q) for pat in _VAGUE_PATTERNS):
        return True

    # pronoun-heavy
    if sum(1 for p in _PRONOUNS if f" {p} " in f" {q} ") >= 1:
        return True

    return False
