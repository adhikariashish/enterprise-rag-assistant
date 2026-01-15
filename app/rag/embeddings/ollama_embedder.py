from __future__ import annotations
from typing import List
from app.rag.embeddings.embedder_base import Embedder
from dataclasses import dataclass
import requests, os

@dataclass
class OllamaEmbedderConfig:
    model_name: str = "nomic-embed-text"
    api_url: str = "http://localhost:11434"
    timeout_s: int = 60


class OllamaEmbedder(Embedder):
    """
    Ollama-based embedding implementation.

    This embedder:
    - uses Ollama's /api/embeddings endpoint
    - produces vectors suitable for Chroma
    - must be used consistently for BOTH:
        - document embeddings (ingest time)
        - query embeddings (runtime)
    """
    def __init__(self, config: OllamaEmbedderConfig):
        self.cfg = config

    def embed_one(self, text: str) -> List[float]:
        """Generate an embedding for a single piece of text using Ollama.
        Args:
            text (str): The input text to embed.
        Returns:
            List[float]: The embedding vector.
        """
        base_url = os.getenv("OLLAMA_API_URL", self.cfg.api_url)
        url = f"{base_url}/api/embeddings"
        payload = {
            "model": self.cfg.model_name,
            "prompt": text
        }
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.cfg.timeout_s
            )

            response.raise_for_status()
            
            data = response.json()
            
            embedding = data["embedding"]
            
            return embedding
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get embedding from Ollama: {e}")