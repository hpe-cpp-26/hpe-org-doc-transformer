from __future__ import annotations


from embedding.embedder import generate_embedding

from .utils import validate_embedding

DOC_PREFIX = "search_document: "


def embed_chunks(chunks: list[dict[str, object]]) -> None:
    for chunk in chunks:
        chunk_text = str(chunk.get("chunk_text", ""))
        embedding = _embed_with_prefix(DOC_PREFIX, chunk_text)
        chunk["embedding"] = embedding
        chunk["embedding_dim"] = len(embedding)


def _embed_with_prefix(prefix: str, text: str) -> list[float]:
    raw = list(generate_embedding(prefix + text))
    validate_embedding(raw)
    return raw