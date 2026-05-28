from __future__ import annotations

import logging

from typing import Any

from db import refresh_buffer_for_doc, refresh_doc_count, count_buffered, fetch_buffer_embeddings
from db.prototypes import upsert_prototypes, clear_buffer, update_proto_count
from .utils import cosine_similarity
from .segments import kmeans, nearest_centroid

logger = logging.getLogger(__name__)



def assign_group(
    doc_id: str,
    group_id: str,
    segments: list[dict[str, Any]],
    conn: Any,
) -> None:
    if not segments:
        logger.warning(
            "assign_group: no segments found for doc_id=%s", doc_id
        )
        return

    refresh_buffer_for_doc(doc_id, group_id, segments, conn)
    refresh_doc_count(group_id, conn)

    buffered = count_buffered(group_id, conn)
    if buffered >= 40:
        embeddings = fetch_buffer_embeddings(group_id, conn)
        prototypes = compute_medoids(embeddings)
        upsert_prototypes(group_id, prototypes, conn)
        clear_buffer(group_id, conn)
        update_proto_count(group_id, len(prototypes), conn)


def compute_medoids(embeddings: list[list[float]]) -> list[list[float]]:
    if not embeddings:
        return []

    n = len(embeddings)

    if n == 1:
        return [embeddings[0]]
    if n == 2:
        return [embeddings[0], embeddings[1]]
    if n == 3:
        return [embeddings[0], embeddings[1], embeddings[2]]


    k = min(5, max(2, n // 10))
    centroids = kmeans(embeddings, k)

    assignments: list[list[int]] = [[] for _ in range(len(centroids))]
    for idx, vec in enumerate(embeddings):
        nearest = nearest_centroid(vec, centroids)
        assignments[nearest].append(idx)

    medoids: list[list[float]] = []
    for cluster_indices in assignments:
        if not cluster_indices:
            continue
        medoids.append(cluster_medoid(embeddings, cluster_indices))

    return medoids


def cluster_medoid(
    embeddings: list[list[float]],
    indices: list[int],
) -> list[float]:
    """
    True medoid — the vector with highest total cosine similarity
    to all other vectors in the cluster.
    Not the nearest-to-centroid shortcut.
    """
    best_idx = indices[0]
    best_score = -1.0

    for idx in indices:
        score = sum(
            cosine_similarity(embeddings[idx], embeddings[other])
            for other in indices
            if other != idx
        )
        if score > best_score:
            best_score = score
            best_idx = idx

    return embeddings[best_idx]

