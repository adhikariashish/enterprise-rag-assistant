# app/rag/prompts/loader.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class PromptBundle:
    system: str
    answer: str
    rewrite: str


class PromptLoader:

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        self._root_dir = root_dir or Path(__file__).resolve().parent
        self._cache: Optional[PromptBundle] = None

    def load(self, force_reload: bool = False) -> PromptBundle:
        if self._cache is not None and not force_reload:
            return self._cache

        system = self._read("system.txt")
        answer = self._read("answer.txt")
        rewrite = self._read("rewrite.txt")

        self._cache = PromptBundle(system=system, answer=answer, rewrite=rewrite)
        return self._cache

    def _read(self, filename: str) -> str:
        path = self._root_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        text = path.read_text(encoding="utf-8")
        return text.strip()
