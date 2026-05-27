

import json

from doc_types.state import ClassifierState
from embedding.embedder import generate_embedding
from db import insert_doc_embedding_cache, search_similar_prototypes
from config.settings import get_settings
import logging 

settings = get_settings()
logger = logging.getLogger(__name__)

def decide_route(state: ClassifierState) -> ClassifierState:
    content = state.get("fingerprint", "")
    if isinstance(content, dict):
        content = content.get("fingerprint", "") or json.dumps(content)
    if content is None:
        content = ""
    embedding = list(generate_embedding("search_query: " + content))
    state["embedding"] = embedding


    #Search for similar group prototypes and aggregate by group.
    prototype_hits = search_similar_prototypes(
        embedding=embedding,
        limit=settings.top_k,
        min_similarity=settings.review_threshold,
    )
    groups = _aggregate_group_candidates(prototype_hits or [])
    state["similar_group_candidates"] = groups
    state["top_similarity_score"] = groups[0]["similarity"] if groups else 0.0
    if not groups:
        state["create_new_group"] = True
        state["classification_route"] = "CREATE_NEW_GROUP"
    elif groups[0]["similarity"] >= settings.auto_assign_threshold:
        state["create_new_group"] = False
        state["classification_route"] = "AUTO_ASSIGN"
        state["existing_group_id"] = groups[0]["id"]
    else:
        state["create_new_group"] = False
        state["similar_group_candidates"] = groups
        state["classification_route"] = "REVIEW_BY_AGENT"

        # Cache the embedding for later use — non-critical, log failures only
        try:
            insert_doc_embedding_cache(state["doc_id"], embedding)
        except Exception as cache_exc:
            logger.warning(
                "decide_route: failed to cache embedding for doc '%s': %s",
                state.get("doc_id"),
                cache_exc,
            )

    return state


def _aggregate_group_candidates(rows: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for row in rows:
        group_id = row.get("id")
        if not group_id:
            continue
        existing = grouped.get(group_id)
        similarity = float(row.get("similarity", 0.0))
        if existing is None or similarity > existing["similarity"]:
            grouped[group_id] = {
                "id": group_id,
                "name": row.get("name"),
                "doc_count": row.get("doc_count"),
                "proto_count": row.get("proto_count"),
                "similarity": similarity,
                "top_proto_index": row.get("proto_index"),
            }

    return sorted(grouped.values(), key=lambda item: item["similarity"], reverse=True)

    
