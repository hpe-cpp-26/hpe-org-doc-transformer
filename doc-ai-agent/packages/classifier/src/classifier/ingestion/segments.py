from typing import Any, Iterable, Mapping, Sequence
import logging
import math
import random
from .utils import l2_normalize, validate_embedding , cosine_similarity, mean_vector

def build_segment_embeddings(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not chunks:
        return []

    n = len(chunks)

    if n <= 4:
        return [_segment_from_chunks(chunks, 0)]

    if n <= 12:
        return _split_segments(chunks, 2)

    if n <= 24:
        return _split_segments(chunks, 3)

    # large doc — semantic clustering
    # min 5 chunks per segment
    n_segments = min(5, max(2, n // 5))
    return _cluster_segments(chunks, n_segments)


def _segment_from_chunks(
    chunks: list[dict[str, Any]],
    segment_index: int,
) -> dict[str, Any]:
    # use embedding (search_document prefix) for pooling
    # word_count as weight so longer chunks contribute more
    pooled = _weighted_pool(
        [chunk["embedding"] for chunk in chunks],
        [max(chunk["word_count"], 1) for chunk in chunks],
    )
    return {
        "segment_index": segment_index,
        "chunk_indices": [chunk["chunk_index"] for chunk in chunks],
        "embedding":     pooled,
    }


def _split_segments(
    chunks: list[dict[str, Any]],
    n_segments: int,
) -> list[dict[str, Any]]:
    size = math.ceil(len(chunks) / n_segments)
    result: list[dict[str, Any]] = []
    for idx in range(n_segments):
        start = idx * size
        end = min(len(chunks), start + size)
        segment_chunks = chunks[start:end]
        if not segment_chunks:
            continue
        result.append(_segment_from_chunks(segment_chunks, idx))
    return result

#groups by semantic similarity of chunk embeddings using k-means clustering
def _cluster_segments(
    chunks: list[dict[str, Any]],
    k: int,
) -> list[dict[str, Any]]:
    vectors = [chunk["embedding"] for chunk in chunks]
    centroids = _kmeans(vectors, k)

    assignments: list[list[int]] = [[] for _ in range(k)]
    for idx, vec in enumerate(vectors):
        nearest = _nearest_centroid(vec, centroids)
        assignments[nearest].append(idx)

    segments: list[dict[str, Any]] = []
    seg_idx = 0
    for cluster_indices in assignments:
        if not cluster_indices:
            continue
        segment_chunks = [chunks[i] for i in cluster_indices]
        segments.append(_segment_from_chunks(segment_chunks, seg_idx))
        seg_idx += 1

    return segments


def _weighted_pool(
    embeddings: Sequence[Sequence[float]],
    weights: Sequence[int],
) -> list[float]:
    """basically a weighted average of the embeddings
    longer chunks contribute more to the segment embedding
    """
    if not embeddings:
        raise ValueError("Cannot pool empty embeddings")

    dim = len(embeddings[0])
    totals = [0.0] * dim
    weight_sum = sum(max(w, 1) for w in weights)

    for emb, w in zip(embeddings, weights):
        if len(emb) != dim:
            raise ValueError("Embedding dimension mismatch during pooling")
        effective_w = max(w, 1)
        for i, val in enumerate(emb):
            totals[i] += float(val) * effective_w

    pooled = [v / weight_sum for v in totals]
    validate_embedding(pooled)
    return l2_normalize(pooled)


def _kmeans(
    vectors: list[list[float]],
    k: int,
    iterations: int = 30,
) -> list[list[float]]:
    if k <= 0:
        raise ValueError("k must be positive")
    k = min(k, len(vectors))

   
    indices = random.sample(range(len(vectors)), k)
    centroids = [vectors[i][:] for i in indices]

    for _ in range(iterations):
        buckets: list[list[list[float]]] = [[] for _ in range(k)]
        for vec in vectors:
            buckets[_nearest_centroid(vec, centroids)].append(vec)

        new_centroids: list[list[float]] = []
        for i, bucket in enumerate(buckets):
            if not bucket:
                new_centroids.append(centroids[i])
            else:
                new_centroids.append(mean_vector(bucket))
        centroids = new_centroids

    return centroids


def _nearest_centroid(
    vec: list[float],
    centroids: list[list[float]],
) -> int:
    best_idx = 0
    best_score = -1.0
    for idx, centroid in enumerate(centroids):
        score = cosine_similarity(vec, centroid)
        if score > best_score:
            best_score = score
            best_idx = idx
    return best_idx

