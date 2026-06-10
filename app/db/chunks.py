from typing import Any

from app.db.utils import (
    Vector,
    _vector_literal,
)

from app.db.connection import (
    get_connection,
    DatabaseConnectionError,
)

import psycopg


def search_similar_chunks(
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
        d.path AS doc_path,
        dc.chunk_text,
        1 - (dc.embedding <=> q.vec) AS similarity
    FROM document_chunks dc
    JOIN documents d
        ON dc.doc_id = d.id
    CROSS JOIN query_vec q
    ORDER BY dc.embedding <=> q.vec
    LIMIT %s
"""

    try:
        with get_connection(autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    [vector, limit]
                )

                rows = cursor.fetchall()

    except psycopg.Error as exc:
        raise DatabaseConnectionError(
            "Chunk similarity search failed"
        ) from exc

    return [dict(row) for row in rows]

