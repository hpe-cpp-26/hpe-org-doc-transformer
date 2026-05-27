from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence


def split_words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def estimate_tokens(word_count: int) -> int:
    return max(1, int(math.ceil(word_count * 0.75)))


def validate_embedding(embedding: Sequence[float]) -> None:
    if len(embedding) != 768:
        raise ValueError(
            f"Expected 768-dimensional embedding, got {len(embedding)}."
        )


def l2_normalize(values: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(float(v) * float(v) for v in values))
    if norm == 0.0:
        raise ValueError("Embedding vector has zero norm and cannot be normalized")
    return [float(v) / norm for v in values]


def mean_vector(vectors: Iterable[Sequence[float]]) -> list[float]:
    vecs = list(vectors)
    if not vecs:
        raise ValueError("Cannot average empty vectors")
    dim = len(vecs[0])
    totals = [0.0] * dim
    for vec in vecs:
        if len(vec) != dim:
            raise ValueError("Embedding dimension mismatch")
        for i, val in enumerate(vec):
            totals[i] += float(val)
    mean = [v / len(vecs) for v in totals]
    validate_embedding(mean)
    return l2_normalize(mean)


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))
