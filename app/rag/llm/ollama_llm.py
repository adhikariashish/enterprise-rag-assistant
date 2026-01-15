from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Iterator
import requests
import json, os

from app.rag.llm.llm_base import LLM

@dataclass
class OllamaLLMConfig:
    model_name: str = "llama3.1:latest"
    api_url: str = "http://localhost:11434"
    timeout_s: int = 120
    temperature: float = 0.2

class OllamaLLM(LLM):
    """
    This class implements the LLM interface to interact with an Ollama server.
    """

    def __init__(self, cfg: OllamaLLMConfig):
        self.cfg = cfg

    def generate(self, prompt: str) -> str:
        """Generate a text completion for the given prompt using Ollama API."""
        base_url = os.getenv("OLLAMA_API_URL", self.cfg.api_url)
        url = f"{base_url}/api/generate"

        payload = {
            "model": self.cfg.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.cfg.temperature,
            },
        }
        response = requests.post(
            url,
            json=payload,
            timeout=self.cfg.timeout_s,
        )
        response.raise_for_status()
        data = response.json()
        if "response" not in data:
            raise RuntimeError(f"Ollama generate response missing 'response': {data}")

        return data["response"].strip()

    #for streaming
    def generate_stream(self, prompt:str) -> Iterator[str]:
        """
            Streaming from Ollama : yields token chunks as they arrive.
        """
        base_url = os.getenv("OLLAMA_API_URL", self.cfg.api_url)
        url = f"{base_url}/api/generate"
        payload = {
            "model": self.cfg.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": self.cfg.temperature,
            },
        }

        with requests.post(url, json=payload, stream = True, timeout=self.cfg.timeout_s) as r:
            r.raise_for_status()

            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                obj = json.loads(line)
                if obj.get("done"):
                    break
                
                chunk = obj.get("response") or ""
                if chunk:
                    yield chunk
        