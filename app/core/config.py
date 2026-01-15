# root/app/core/config.py
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal

import yaml
import os
from pydantic import BaseModel, Field


# ---------- YAML loading + merging ----------

def _repo_root() -> Path:
    # root redirect
    return Path(__file__).resolve().parents[2]

def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Top-level YAML must be a mapping/dict: {path}")
    return data


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_all_configs() -> Dict[str, Any]:
    """
    Merge multiple YAML files under root/configs into one dict.
    Missing files are ignored so can be added gradually.
    """
    cfg_dir = _repo_root() / "configs"
    # print("DEBUG cfg_dir: ", cfg_dir)
    filenames = ["app.yaml", "providers.yaml", "ollama.yaml", "rag.yaml", "policy.yaml"]

    merged: Dict[str, Any] = {}
    for name in filenames:
        merged = _deep_merge(merged, _load_yaml(cfg_dir / name))

    return merged


# ---------- Pydantic Settings models ----------

class AppConfig(BaseModel):
    app_name: str = "Consultancy RAG Bot"
    log_level: str = "INFO"
    env: str = "dev"
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])


class ProvidersConfig(BaseModel):
    llm: Literal["ollama", "openai"] = "ollama"
    embedder: Literal["ollama", "openai"] = "ollama"
    store: Literal["chroma", "faiss"] = "chroma"


class OllamaLLMConfig(BaseModel):
    model_name: str = "mistral:7b-instruct-q4_0"
    temperature: float = 0.1
    api_url: str = "http://127.0.0.1:11434"
    timeout_s: int = 120


class OllamaEmbeddingsConfig(BaseModel):
    model_name: str = "nomic-embed-text"
    


class OllamaConfig(BaseModel):
    api_url: str = "http://127.0.0.1:11434"
    timeout_s: int = 60
    llm: OllamaLLMConfig = Field(default_factory=OllamaLLMConfig)
    embeddings: OllamaEmbeddingsConfig = Field(default_factory=OllamaEmbeddingsConfig)


class RagRewriteConfig(BaseModel):
    enabled: bool = True
    trigger_max_words: int = 8
    max_history_turns: int = 6


class RagDistanceConfig(BaseModel):
    good_threshold: float = 0.40
    weak_threshold: float = 0.55


class RagConfig(BaseModel):
    collection_name: str = "consultancy_kb"
    persist_dir: str = "storage/vectordb"
    top_k: int = 5
    retrieval_pool_k: int = 25
    max_context_chars: int = 3000
    max_chunks_in_prompt: int = 3
    max_history: int = 6
    distance: RagDistanceConfig = Field(default_factory=RagDistanceConfig)
    rewrite: RagRewriteConfig = Field(default_factory=RagRewriteConfig)


class PolicyConfig(BaseModel):
    deny_message: str = "I couldn't find relevant information in the knowledge base."
    system_style: str = "clear, concise, policy-style"
    require_quotes_in_weak_mode: bool = True


class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    rag: RagConfig = Field(default_factory=RagConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    raw = load_all_configs()
    return Settings.model_validate(raw)
