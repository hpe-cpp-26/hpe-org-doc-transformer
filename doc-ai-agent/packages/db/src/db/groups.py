
from typing import Any
from .utils import Vector, _run_write, _vector_literal
from .connection import get_connection, DatabaseConnectionError
import psycopg



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
        with get_connection(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Prototype similarity search failed") from exc

    return [dict(row) for row in rows]

def search_similar_buffer(
    embedding: Vector,
    *,
    limit: int = 20,
    min_similarity: float = 0.4,
) -> list[dict[str, Any]]:
    vector = _vector_literal(embedding)

    query = """
        WITH query_vec AS (
            SELECT %s::vector AS vec
        )
        SELECT
            pb.group_id AS id,
            g.group_name AS name,
            g.doc_count,
            g.proto_count,
            pb.segment_index AS proto_index,
            1 - (pb.embedding <=> q.vec) AS similarity
        FROM prototype_buffer pb
        JOIN groups g ON g.id = pb.group_id
        JOIN query_vec q ON TRUE
        WHERE 1 - (pb.embedding <=> q.vec) >= %s
        ORDER BY pb.embedding <=> q.vec
        LIMIT %s
    """

    params: list[Any] = [vector, min_similarity, limit]

    try:
        with get_connection(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Buffer similarity search failed") from exc

    return [dict(row) for row in rows]


def search_similar_segments(
    embedding: Vector,
    *,
    limit: int = 20,
    min_similarity: float = 0.35,
) -> list[dict[str, Any]]:
    vector = _vector_literal(embedding)

    query = """
        WITH query_vec AS (
            SELECT %s::vector AS vec
        )
        SELECT
            ds.group_id AS id,
            g.group_name AS name,
            g.doc_count,
            g.proto_count,
            ds.segment_index AS proto_index,
            1 - (ds.embedding <=> q.vec) AS similarity
        FROM document_segments ds
        JOIN groups g ON g.id = ds.group_id
        JOIN query_vec q ON TRUE
        WHERE ds.group_id IS NOT NULL
        AND 1 - (ds.embedding <=> q.vec) >= %s
        ORDER BY ds.embedding <=> q.vec
        LIMIT %s
    """

    params: list[Any] = [vector, min_similarity, limit]

    try:
        with get_connection(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Segment similarity search failed") from exc

    return [dict(row) for row in rows]

def insert_new_group(
    group_id: str,
    group_name: str,
    group_summary: str,
    conn: Any | None = None,
) -> None:
    query = """
        INSERT INTO groups (id, group_name, group_summary, doc_count, proto_count)
        VALUES (%s, %s, %s, 0, 0)
        ON CONFLICT (id) DO NOTHING
    """
    params = [group_id, group_name, group_summary]

    if conn is None:
        _run_write(query, params)
        return

    with conn.cursor() as cursor:
        cursor.execute(query, params)
    