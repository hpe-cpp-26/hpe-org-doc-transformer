"""Generate 768-dimensional embeddings using Ollama."""

import os
from typing import Sequence

from config.settings import get_settings
import requests


def generate_embedding(text: str) -> Sequence[float]:
    """
    Generate a 768-dimensional embedding for the given text using Ollama.
    
    Args:
        text: The text to embed
        
    Returns:
        A list of 768 floats representing the embedding
        
    Raises:
        ConnectionError: If Ollama is not reachable
        ValueError: If the embedding dimension is not 768
    """
    def get_env_url(name:str) -> str:
        return get_settings().name
    
    # ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    # model = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

    ollama_host = get_env_url("OLLAMA_HOST") or "http://localhost:11434"
    model = get_env_url("EMBEDDING_MODEL") or "nomic-embed-text"
    try:
        response = requests.post(
            f"{ollama_host}/api/embed",
            json={
                "model": model,
                "input": text,
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ConnectionError(
            f"Failed to reach Ollama at {ollama_host}. "
            "Make sure Ollama is running: ollama serve"
        ) from exc
    
    data = response.json()
    embeddings = data.get("embeddings", [])
    
    if not embeddings:
        raise ValueError("No embeddings returned from Ollama")
    
    embedding = embeddings[0]
    
    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768-dimensional embedding, got {len(embedding)}. "
            f"Ensure the model '{model}' outputs 768 dimensions."
        )
    
    return embedding
