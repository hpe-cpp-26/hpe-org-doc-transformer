from typing import Sequence

import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)


def generate_embedding(
    text: str,
) -> Sequence[float]:

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/embed",
            json={
                "model": EMBEDDING_MODEL,
                "input": text,
            },
            timeout=60,
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        raise ConnectionError(
            f"Failed to reach Ollama at {OLLAMA_HOST}"
        ) from exc

    data = response.json()

    embeddings = data.get(
        "embeddings",
        []
    )

    if not embeddings:
        raise ValueError(
            "No embeddings returned from Ollama"
        )

    embedding = embeddings[0]

    return embedding