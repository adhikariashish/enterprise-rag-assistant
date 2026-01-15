from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from app.core.config import get_settings
from app.rag.embeddings.embedder_base import Embedder
from app.rag.llm.llm_base import LLM

from app.rag.embeddings.ollama_embedder import OllamaEmbedder, OllamaEmbedderConfig
from app.rag.llm.ollama_llm import OllamaLLM, OllamaLLMConfig


def create_embedder() -> Embedder:
    settings = get_settings()

    if settings.providers.embedder == "ollama":
        return OllamaEmbedder(
            OllamaEmbedderConfig(
                model_name=settings.ollama.embeddings.model_name,
                api_url=settings.ollama.api_url,
                timeout_s=settings.ollama.timeout_s,
            )
        )

    if settings.providers.embedder == "openai":
        raise NotImplementedError("OpenAI embedder provider not implemented yet.")

    raise ValueError(f"Unknown embedder provider: {settings.providers.embedder}")


def create_llm() -> LLM:
    settings = get_settings()

    if settings.providers.llm == "ollama":
        return OllamaLLM(
            OllamaLLMConfig(
                model_name=settings.ollama.llm.model_name,
                api_url=settings.ollama.api_url,
                temperature=settings.ollama.llm.temperature,
                timeout_s=settings.ollama.timeout_s,
            )
        )

    if settings.providers.llm == "openai":
        raise NotImplementedError("OpenAI LLM provider not implemented yet.")

    raise ValueError(f"Unknown llm provider: {settings.providers.llm}")


def create_providers() -> Tuple[Embedder, LLM]:
    return create_embedder(), create_llm()
