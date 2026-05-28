

import json

from doc_types.state import ClassifierState
from embedding.embedder import generate_embedding
from db import insert_doc_embedding_cache, search_similar_prototypes, search_similar_buffer, search_similar_segments
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

    groups = search_similar_groups(embedding)
   
    state["similar_group_candidates"] = groups[:settings.min_groups_for_review] if len(groups) >= settings.min_groups_for_review else groups
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
        state["classification_route"] = "REVIEW_BY_AGENT"

       
        try:
            insert_doc_embedding_cache(state["doc_id"], embedding)
        except Exception as cache_exc:
            logger.warning(
                "decide_route: failed to cache embedding for doc '%s': %s",
                state.get("doc_id"),
                cache_exc,
            )

    return state


def search_similar_groups(embedding: list[float]) -> list[dict]:

    #prototype hits
    similar_prototypes =search_similar_prototypes(
        embedding=embedding,
        limit=20,
        min_similarity=settings.review_threshold)
    
    proto_groups = aggregate_group_candidates(similar_prototypes or [])
    if len(proto_groups) >=settings.min_groups_for_review:
        return proto_groups

    #buffer hits
    similar_bufffers = search_similar_buffer(
        embedding=embedding,
        limit=20,
        min_similarity=settings.review_threshold-0.02
        )
    buffer_groups = aggregate_group_candidates(similar_bufffers or [])


    merged = merge_group_candidates(proto_groups, buffer_groups)
    if len(merged) >= settings.min_groups_for_review:
        return merged


    #segment hits
    similar_segments = search_similar_segments(
        embedding=embedding,
        limit=20,
        min_similarity=settings.review_threshold-0.05
    )
    segment_groups = aggregate_group_candidates(similar_segments or [])

    return merge_group_candidates(merged, segment_groups)



def aggregate_group_candidates(rows: list[dict]) -> list[dict]:
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


def merge_group_candidates(primary: list[dict], fallback: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {g["id"]: g for g in primary}

    for group in fallback:
        group_id = group["id"]
        if group_id not in merged:
            merged[group_id] = group
        elif group["similarity"] > merged[group_id]["similarity"]:
            merged[group_id] = group

    return sorted(merged.values(), key=lambda g: g["similarity"], reverse=True)


