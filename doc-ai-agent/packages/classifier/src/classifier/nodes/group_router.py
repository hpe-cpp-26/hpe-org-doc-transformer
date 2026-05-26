

import json

from doc_types.state import ClassifierState
from embedding.embedder import generate_embedding
from db.vector_queries import insert_doc_embedding_cache, search_similar_centroid
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
    embedding = list(generate_embedding(content))
    state["embedding"] = embedding


    #Search for similar centroid groups.
    groups = search_similar_centroid(
        embedding=embedding,
        limit=settings.top_k,
        min_similarity=settings.review_threshold,
    )
    groups = groups or []
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

    
