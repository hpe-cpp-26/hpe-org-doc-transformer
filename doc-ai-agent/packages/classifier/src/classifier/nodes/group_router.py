

from doc_types.state import ClassifierState
from embedding.embedder import generate_embedding
from db.vector_queries import search_similar_centroid
from config.settings import get_settings

settings = get_settings()

def decide_route(state: ClassifierState) -> ClassifierState:
    content = state.get("content", "")
    embedding = generate_embedding(content)
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
        state["existing_group_id"] = groups[0]["group_id"]
    else:
        state["create_new_group"] = False
        state["classification_route"] = "REVIEW_BY_AGENT"


    state["decision_path"].append("decide_route")
    return state

    
