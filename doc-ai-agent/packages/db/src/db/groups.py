
from typing import Any
from .utils import Vector, _run_write, _vector_literal
from .connection import get_connection, DatabaseConnectionError
import psycopg


def search_similar_centroid(
    embedding: Vector,
    *,
    limit: int = 10,
    min_similarity: float = 0.4,
) -> list[dict[str, Any]]:
    vector = _vector_literal(embedding)
    
    query = """
        WITH query_vec AS (
            SELECT %s::vector AS vec
        )
        SELECT
            g.id,
            g.name,
            g.doc_count,
            1 - (g.centroid <=> q.vec) AS similarity
        FROM groups g, query_vec q
        WHERE g.centroid IS NOT NULL
        AND 1 - (g.centroid <=> q.vec) >= %s
        ORDER BY g.centroid <=> q.vec
        LIMIT %s
    """
    
    params: list[Any] = [vector, min_similarity, limit]
   
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Similarity search failed") from exc

    return [dict(row) for row in rows]


def search_similar_prototypes(
    embedding: Vector,
    *,
    limit: int = 10,
    min_similarity: float = 0.4,
) -> list[dict[str, Any]]:
    vector = _vector_literal(embedding)

    query = """
        WITH query_vec AS (
            SELECT %s::vector AS vec
        )
        SELECT
            gp.group_id AS id,
            g.group_name AS name,
            g.doc_count,
            g.proto_count,
            gp.proto_index,
            1 - (gp.embedding <=> q.vec) AS similarity
        FROM group_prototypes gp
        JOIN groups g ON g.id = gp.group_id
        JOIN query_vec q ON TRUE
        WHERE 1 - (gp.embedding <=> q.vec) >= %s
        ORDER BY gp.embedding <=> q.vec
        LIMIT %s
    """

    params: list[Any] = [vector, min_similarity, limit]

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Prototype similarity search failed") from exc

    return [dict(row) for row in rows]



def update_centroid(
    group_id: str,
    centroid: Vector,
    *,
    doc_count: int | None = None,
) -> None:
    assignments = ["centroid = %s::vector"]
    params: list[Any] = [_vector_literal(centroid)]

    if doc_count is not None:
        assignments.append("doc_count = %s")
        params.append(doc_count)

    params.append(group_id)

    _run_write(
        f"""
        UPDATE groups
        SET {", ".join(assignments)}
        WHERE id = %s
        """,
        params,
    )

def insert_new_group(
        group_id: str,
        group_name: str,
        group_summary: str,
) -> None:
    _run_write(
        """
        INSERT INTO groups (id, group_name, group_summary, doc_count, proto_count)
        VALUES (%s, %s, %s, 0, 0)
        ON CONFLICT (id) DO NOTHING
        """,
        [group_id, group_name, group_summary]
    )
    