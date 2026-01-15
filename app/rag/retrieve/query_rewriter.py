from typing import List
from app.rag.policy.rewrite_rules import should_rewrite
from dataclasses import dataclass
from app.api.schemas import ChatTurn
from app.rag.llm.llm_base import LLM
import re

@dataclass(frozen=True)
class QueryRewriterConfig:
    enabled: bool
    max_history_turns: int
    trigger_max_words: int
    max_rewrite_chars: int = 300


class QueryRewriter:
    """
        Decide whether to rewrite the question for clarity, and do so if needed.
        Rewrite the question using the LLM to add context from history.

    """

    def __init__ (self, *, llm, rewrite_template:str, cfg: QueryRewriterConfig) -> None:
        self.llm = llm
        self.rewrite_template = (rewrite_template or "").strip()
        self.cfg = cfg

    def maybe_rewrite(self, question: str, history_text: str) ->  str:
        # check for reasons to rewrite
        if not self.cfg.enabled:
            return question
        
        if not should_rewrite(question, self.cfg.trigger_max_words):
            return question
        
        if not (history_text or "").strip():
            return question
        
        prompt = self.rewrite_template.format(history=history_text, question=question)
        rewritten = (self.llm.generate(prompt) or "").strip()

        # safety fallback: if llm fails to rewrite or return empty/junk/multi-line, take either first like or fallback
        rewritten = (rewritten.splitlines()[0].strip() if rewritten else " ").strip()
        if not rewritten:
            return question
        
        # if it rewrites too aggressively , keep it bounded 
        if len(rewritten) > self.cfg.max_rewrite_chars:
            return question 
        
        return rewritten

