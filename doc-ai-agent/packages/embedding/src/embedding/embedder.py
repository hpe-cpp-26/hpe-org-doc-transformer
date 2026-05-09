from typing import Sequence

import logging
import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def generate_embedding(text: str) -> Sequence[float]:
    """Generates a 768-dimensional embedding for the given text."""

    try:
        response = requests.post(
            f"{settings.ollama_host}/api/embed",
            json={
                "model": settings.embedding_model,
                "input": text,
            },
            timeout=60,
        )
        logger.debug(f"Received response from Ollama", extra={"status_code": response.status_code, "response": response.text})
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"Error connecting to Ollama", extra={"error": str(exc)})
        raise ConnectionError(
            f"Failed to reach Ollama at {settings.ollama_host}. "
            "Make sure Ollama is running: ollama serve"
        ) from exc
    
    data = response.json()
    embeddings = data.get("embeddings", [])
    
    if not embeddings:
        logger.error(f"No embeddings returned from Ollama")
        raise ValueError("No embeddings returned from Ollama")
    
    embedding = embeddings[0]
    
    if len(embedding) != 768:
        logger.error(f"Unexpected embedding dimension", extra={"embedding": embedding})
        raise ValueError(
            f"Expected 768-dimensional embedding, got {len(embedding)}. "
        )
    
    return embedding
