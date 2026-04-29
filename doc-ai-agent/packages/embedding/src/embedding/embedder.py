from typing import Sequence

from config.settings import get_settings
import requests
import logging

logger = logging.getLogger(__name__)

def get_env(name: str) -> str | None:
    settings = get_settings()
    return getattr(settings, name, None)
    

ollama_host = get_env("OLLAMA_HOST")
model = get_env("EMBEDDING_MODEL")

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

    try:
        response = requests.post(
            f"{ollama_host}/api/embed",
            json={
                "model": model,
                "input": text,
            },
            timeout=60,
        )
        logger.debug(f"Received response from Ollama", extra={"status_code": response.status_code, "response": response.text})
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"Error connecting to Ollama", extra={"error": str(exc)})
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
        logger.error(f"Unexpected embedding dimension", extra={"embedding": embedding})
        raise ValueError(
            f"Expected 768-dimensional embedding, got {len(embedding)}. "
        )
    
    return embedding
