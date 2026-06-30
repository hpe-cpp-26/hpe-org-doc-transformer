import logging
from typing import Any

import psycopg
from langsmith import traceable

from app.db.connection import get_connection, DatabaseConnectionError
from app.db.utils import _vector_literal
from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_chunks

logger = logging.getLogger(__name__)

class ResultList(list):
    def __init__(self, data, **kwargs):
        super().__init__(data)
        for k, v in kwargs.items():
            setattr(self, k, v)

@traceable
def embed_query(query: str) -> list[float]:
    """
    Embed the incoming query using the SAME model used at ingestion.
    Model must produce VECTOR(768) output.
    Return as a plain Python list of floats — pgvector expects this format.
    """
    return list(generate_embedding(query))

@traceable
def search_group_prototypes(
    query_embedding: list[float],
    top_k: int = 5,
    similarity_threshold: float = 0.55
) -> list[str]:
    """
    Search group_prototypes for the closest prototype embeddings to the query.
    Return a deduplicated list of group_ids ranked by best prototype match per group.
    union with protoype_buffer to also consider recently added prototypes that haven't been merged yet.
    """
    vector = _vector_literal(query_embedding)
    
    query = """
        SELECT * FROM (
            SELECT DISTINCT ON (group_id)
                   group_id,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM (
                SELECT group_id, embedding FROM group_prototypes
                UNION ALL
                SELECT group_id, embedding FROM prototype_buffer
            ) combined
            ORDER  BY group_id, embedding <=> %s::vector ASC
        ) sub
        ORDER BY similarity DESC
    """
    
    try:
        with get_connection(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, [vector, vector])
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Group prototype search failed") from exc

    results = []
    similarities = []
    for row in rows:
        if row["similarity"] >= similarity_threshold:
            results.append(row["group_id"])
            similarities.append(row["similarity"])
            
    # fallback to return top 2 when no results meet the threshold
    if not results and rows:
        results = [row["group_id"] for row in rows[:2]]
        similarities = [row["similarity"] for row in rows[:2]]

    return ResultList(results[:top_k], similarities=similarities[:top_k])

@traceable
def search_document_chunks(
    query_embedding: list[float],
    group_ids: list[str] | None,
    query: str,
    top_k_retrieve: int = 40,
    top_k_return: int = 7
) -> list[dict]:
    """
    Within shortlisted groups, retrieve the most relevant chunks.
    Then rerank and return top_k_return chunks.
    """
    if group_ids is not None and not group_ids:
        return ResultList([], retrieved_count=0)

    vector = _vector_literal(query_embedding)
    
    if group_ids is None:
        sql_query = """
            SELECT
                dc.id AS chunk_id,
                dc.doc_id,
                dc.chunk_index,
                dc.total_chunks,
                dc.chunk_text,
                d.doc_path,
                d.group_id,
                1 - (dc.embedding <=> %s::vector) AS similarity
            FROM   document_chunks dc
            JOIN   documents d ON d.id = dc.doc_id
            ORDER  BY dc.embedding <=> %s::vector ASC
            LIMIT  %s
        """
        params = [vector, vector, top_k_retrieve]
    else:
        #return from all groups that are above threshold
        sql_query = """
            SELECT
                dc.id AS chunk_id,
                dc.doc_id,
                dc.chunk_index,
                dc.total_chunks,
                dc.chunk_text,
                d.doc_path,
                d.group_id,
                1 - (dc.embedding <=> %s::vector) AS similarity
            FROM   document_chunks dc
            JOIN   documents d ON d.id = dc.doc_id
            WHERE  d.group_id = ANY(%s)
            ORDER  BY dc.embedding <=> %s::vector ASC
            LIMIT  %s
        """
        params = [vector, group_ids, vector, top_k_retrieve]
    
    try:
        with get_connection(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Document chunk search failed") from exc

    chunks = [dict(row) for row in rows]
    retrieved_count = len(chunks)
    
    for c in chunks:
        c["vector_similarity"] = float(c.pop("similarity", 0.0))

    if not chunks:
        return ResultList([], retrieved_count=0)

    #Reranking
    reranked_chunks = rerank_chunks(
        query=query,
        chunks=chunks,
        top_k=len(chunks)
    )
    
    for chunk in reranked_chunks:
        chunk['rerank_score'] = float(chunk.pop('cross_encoder_score', 0.0))

    #deduplication
    doc_path_counts = {}
    final_chunks = []
    for chunk in reranked_chunks:
        doc_path = chunk["doc_path"]
        if doc_path_counts.get(doc_path, 0) < 2:
            final_chunks.append(chunk)
            doc_path_counts[doc_path] = doc_path_counts.get(doc_path, 0) + 1
        
        if len(final_chunks) == top_k_return:
            break

    return ResultList(final_chunks, retrieved_count=retrieved_count)

def build_sources(chunks: list[dict]) -> dict:
    """
    Deduplicate chunks by doc_path and build the sources list
    for the LLM prompt's {context} and {sources} variables.
    """
    doc_path_to_chunks = {}
    
    #group by doc_path
    for chunk in chunks:
        doc_path = chunk["doc_path"]
        if doc_path not in doc_path_to_chunks:
            doc_path_to_chunks[doc_path] = []
        doc_path_to_chunks[doc_path].append(chunk)
        
    context_blocks = []
    citation_map = {}
    source_index = 1
    
    # We want to iterate docs in order of their best chunk's rank
    # So we sort doc_paths based on the position of their first chunk in `chunks`
    doc_paths_ordered = []
    seen = set()
    for c in chunks:
        if c["doc_path"] not in seen:
            doc_paths_ordered.append(c["doc_path"])
            seen.add(c["doc_path"])

    for doc_path in doc_paths_ordered:
        if source_index > 5:
            break
            
        doc_chunks = doc_path_to_chunks[doc_path]
        doc_chunks.sort(key=lambda x: x["chunk_index"])
        merged_text = "\n\n".join(c["chunk_text"] for c in doc_chunks)
        group_id = doc_chunks[0]["group_id"]
        
        best_sim = max((c.get("rerank_score", c.get("vector_similarity", 0.0)) for c in doc_chunks), default=0.0)
        
        context_blocks.append({
            "source_index": source_index,
            "doc_path": doc_path,
            "group_id": group_id,
            "text": merged_text,
            "best_similarity": best_sim
        })
        citation_map[source_index] = doc_path
        source_index += 1
        
    return {
        "context_blocks": context_blocks,
        "citation_map": citation_map
    }

def calculate_retrieval_confidence(
    tier1_results: list[str],
    tier1_similarities: list[float],
    final_chunks: list[dict]
) -> dict:
    """
    Compute a retrieval-side confidence score BEFORE the LLM sees the context.
    mainly to prevent LLM from hallucinating an answer when retrieval is very weak, 
    and to provide a signal to the LLM to calibrate its answer and citations accordingly.
    """
    top_prototype_sim = max(tier1_similarities) if tier1_similarities else 0.0
    top_chunk_rerank = max((c.get("rerank_score", 0.0) for c in final_chunks), default=0.0)
    top_chunk_vec_sim = max((c.get("vector_similarity", 0.0) for c in final_chunks), default=0.0)
    
    unique_sources = len(set(c["doc_path"] for c in final_chunks))
    
    tier_drop_flag = False
    if top_prototype_sim - top_chunk_vec_sim > 0.20:
        tier_drop_flag = True

    score = 0
    band = "LOW"
    reason = "Weak match overall."

    if top_prototype_sim > 0.72 and top_chunk_rerank > 0.80 and unique_sources >= 2:
        band = "HIGH"
        score = 90
        reason = f"Strong prototype match, {unique_sources} corroborating sources"
    elif top_prototype_sim > 0.55 and top_chunk_rerank > 0.55:
        band = "MEDIUM"
        score = 70
        reason = "Moderate matches found, relevance may vary"
    else:
        band = "LOW"
        score = 30
        if top_prototype_sim <= 0.55:
            reason = "Weak prototype match — query may not align with any group topic"
        else:
            reason = "Weak evidence returned at the chunk level"
            
    if tier_drop_flag and band != "LOW":
        score -= 15
        if score < 50:
            band = "LOW"
            reason += " (Significant similarity drop between tiers)"

    return {
        "band": band,
        "score": max(0, min(100, score)),
        "signals": {
            "top_prototype_sim": float(top_prototype_sim),
            "top_chunk_vec_sim": float(top_chunk_vec_sim),
            "top_chunk_rerank": float(top_chunk_rerank),
            "source_diversity": int(unique_sources),
            "tier_drop_flag": bool(tier_drop_flag)
        },
        "reason": reason
    }

@traceable
def retrieve(query: str) -> dict:
    """
    Full retrieval pipeline. This is the single entry point called by the RAG application.
    """
    query_vec = embed_query(query)
    
    tier1_groups = search_group_prototypes(query_vec)
    tier1_similarities = getattr(tier1_groups, "similarities", [])

    if not tier1_groups:
        logger.warning("No tier 1 group prototypes matched. Falling back to global chunk search.")

    final_chunks = search_document_chunks(
        query_vec, 
        group_ids=None if not tier1_groups else tier1_groups, 
        query=query
    )
    chunks_retrieved = getattr(final_chunks, "retrieved_count", 0)
    
    if not final_chunks:
        return {
            "query": query,
            "context_blocks": [],
            "citation_map": {},
            "retrieval_confidence": {
                "band": "LOW",
                "score": 15,
                "signals": {},
                "reason": "No relevant chunks found."
            },
            "debug": {
                "tier1_groups": list(tier1_groups),
                "tier1_similarities": tier1_similarities,
                "chunks_retrieved": chunks_retrieved,
                "chunks_returned": 0
            }
        }

    sources = build_sources(final_chunks)
    
    confidence = calculate_retrieval_confidence(
        tier1_results=tier1_groups,
        tier1_similarities=tier1_similarities,
        final_chunks=final_chunks
    )

    return {
        "query": query,
        "context_blocks": sources["context_blocks"],
        "citation_map": sources["citation_map"],
        "retrieval_confidence": confidence,
        "debug": {
            "tier1_groups": list(tier1_groups),
            "tier1_similarities": tier1_similarities,
            "chunks_retrieved": chunks_retrieved,
            "chunks_returned": len(final_chunks)
        }
    }