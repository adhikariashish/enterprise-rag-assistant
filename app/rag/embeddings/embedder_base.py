from __future__ import annotations
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class Embedder(ABC):
    """Abstract base class for embedding models."""

    @abstractmethod
    def embed_one(self, text: str) -> List[float]:
        """Generate an embedding for a single piece of text.

        Args:
            text (str): The input text to embed.
        Returns:
            List[float]: The embedding vector.
        pass
        """
        raise NotImplementedError

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple pieces of text.

        Args:
            texts (List[str]): A list of input texts to embed.
        Returns:
            List[List[float]]: A list of embedding vectors.
        """
        return [self.embed_one(text) for text in texts]

