from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import psycopg

from .connection import DatabaseConnectionError, get_connection
from doc_types.documents import DocumentAssignment

Vector = Sequence[float | int]


def _vector_literal(values: Vector) -> str:
    """
    pgvector expects vector literals in the formal format: '[0.1, 0.2, 0.3]'.
    """
    if not values:
        raise ValueError("Embedding vectors cannot be empty")
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def _run_write(query: str, params: Sequence[Any]) -> None:
    try:
        with get_connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Database write failed") from exc


def search_similar_centroid(
    embedding: Vector,
    *,  #this ensures that limit and min_similarity must be passed as keyword arguments, not positionally
    limit: int = 10,
    min_similarity: float | None = None,
) -> list[dict[str, Any]]:
    vector = _vector_literal(embedding)
    query = """
        SELECT
            id,
            name,
            centroid,
            doc_count,
            1 - (centroid <=> %s::vector) AS similarity
        FROM groups
        WHERE centroid IS NOT NULL
    """
    params: list[Any] = [vector]

    if min_similarity is not None:
        query += "\n        AND (1 - (centroid <=> %s::vector)) >= %s"
        params.extend([vector, min_similarity])

    query += """
        ORDER BY centroid <=> %s::vector
        LIMIT %s
    """
    params.extend([vector, limit])

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Similarity search failed") from exc

    return [dict(row) for row in rows]


def insert_document(
    document_id: str,
    path: str | None,
    group_id: str | None,
    content: str | None,
    embedding: Vector,
) -> None:
    """Upsert a document and its embedding. 
       If the document ID already exists, all fields will be overwritten with 
       the new values.

       EXCLUDE : special temporary table that holds the values proposed for insertion in case of a conflict.
    """
    _run_write(
        """
        INSERT INTO documents (id, path, group_id, content, embedding, updated_at)
        VALUES (%s, %s, %s, %s, %s::vector, NOW())
        ON CONFLICT (id) DO UPDATE SET
            path = EXCLUDED.path,
            group_id = EXCLUDED.group_id,
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding,
            updated_at = NOW()
        """,
        [document_id, path, group_id, content, _vector_literal(embedding)],
    )


def get_document_assignment(document_id: str) ->DocumentAssignment:
    query = "SELECT group_id, embedding, path FROM documents WHERE id = %s"

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, [document_id])
                row = cursor.fetchone()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Document lookup failed") from exc

    if not row:
        return DocumentAssignment(group_id=None, embedding=None, path=None)

    return DocumentAssignment(
        group_id=row.get("group_id"),
        embedding=row.get("embedding"),
        path=row.get("path")
    )

def update_document(
    document_id: str,
    *,
    path: str | None = None,
    group_id: str | None = None,
    content: str | None = None,
    embedding: Vector | None = None,
) -> None:
    assignments: list[str] = []
    params: list[Any] = []

    if path is not None:
        assignments.append("path = %s")
        params.append(path)
    if group_id is not None:
        assignments.append("group_id = %s")
        params.append(group_id)
    if content is not None:
        assignments.append("content = %s")
        params.append(content)
    if embedding is not None:
        assignments.append("embedding = %s::vector")
        params.append(_vector_literal(embedding))

    if not assignments:
        raise ValueError("At least one field must be supplied when updating a document")

    assignments.append("updated_at = NOW()")
    params.append(document_id)


    # all the values in params list will be substituted 
    # for the %s placeholders in the query string, in order.
    _run_write(
        f"""
        UPDATE documents
        SET {", ".join(assignments)}
        WHERE id = %s
        """,
        params,
    )


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