from typing import Any, Iterable, Mapping
from db.utils import Vector, _vector_literal
from db.connection import get_connection, DatabaseConnectionError
import psycopg

def insert_chunks(
    chunks: Iterable[Mapping[str, Any]],
) -> None:
    rows = [
        (
            chunk["doc_id"],
            chunk["group_id"],
            chunk["chunk_text"],
            _vector_literal(chunk["embedding"]),
        )
        for chunk in chunks
    ]

    if not rows:
        return

    try:
        with get_connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO document_chunks (doc_id, group_id, chunk_text, embedding)
                        VALUES (%s, %s, %s, %s::vector)
                        """,
                        rows,
                    )
    except psycopg.Error as exc:  
        raise DatabaseConnectionError("Chunk insertion failed") from exc
    

def search_similar_chunks_by_group(
    group_id: str,
    embedding: Vector,
    limit: int = 5,
) -> list[dict[str, Any]]:
    vector = _vector_literal(embedding)
    query = """
        WITH query_vec AS (
            SELECT %s::vector AS vec
        )
        SELECT
            dc.doc_id,
            dc.chunk_text,
            1 - (dc.embedding <=> q.vec) AS similarity
        FROM document_chunks dc, query_vec q
        WHERE dc.group_id = %s
        ORDER BY dc.embedding <=> q.vec
        LIMIT %s
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, [vector, group_id, limit])
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Chunk similarity search failed") from exc

    return [dict(row) for row in rows]
