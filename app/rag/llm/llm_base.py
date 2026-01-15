from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

class LLM(ABC):
    """
    Base interface for language models.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text completion for the given prompt."""
        raise NotImplementedError

    @abstractmethod
    def generate_stream(self, prompt:str) -> Iterator[str]:
        
        # Default fallback
        yield self.generate(prompt)

