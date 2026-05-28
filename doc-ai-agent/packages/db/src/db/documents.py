from db.utils import Vector, _run_write
from db.connection import get_connection, DatabaseConnectionError
from db.cache import fetch_embedding_from_cache, insert_doc_embedding_cache
from doc_types.documents import DocumentAssignment
import psycopg
from typing import Any



def insert_document(
    document_id: str,
    doc_path: str | None,
    group_id: str | None,
    content: str | None,
    *,
    segment_count: int = 1,
    embedding: Vector | None = None,
) -> None:
    """Upsert a document and optionally cache its embedding."""
    _run_write(
        """
        INSERT INTO documents (id, doc_path, group_id, content, segment_count, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (id) DO UPDATE SET
            doc_path = EXCLUDED.doc_path,
            group_id = EXCLUDED.group_id,
            content = EXCLUDED.content,
            segment_count = EXCLUDED.segment_count,
            updated_at = NOW()
        """,
        [document_id, doc_path, group_id, content, segment_count],
    )

    if embedding is not None:
        insert_doc_embedding_cache(document_id, embedding)


def get_document_assignment(document_id: str) -> DocumentAssignment:
    query = "SELECT group_id, doc_path FROM documents WHERE id = %s"

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
        path=row.get("doc_path"),
    )

#[TODO: Dharshan][high] fix document update
def update_document(
    document_id: str,
    *,
    doc_path: str | None = None,
    group_id: str | None = None,
    content: str | None = None,
    embedding: Vector | None = None,
    segment_count: int | None = None,
) -> None:
    assignments: list[str] = []
    params: list[Any] = []

    if doc_path is not None:
        assignments.append("doc_path = %s")
        params.append(doc_path)
    if group_id is not None:
        assignments.append("group_id = %s")
        params.append(group_id)
    if content is not None:
        assignments.append("content = %s")
        params.append(content)
    if segment_count is not None:
        assignments.append("segment_count = %s")
        params.append(segment_count)
    if embedding is not None:
        insert_doc_embedding_cache(document_id, embedding)

    if not assignments:
        raise ValueError("At least one field must be supplied when updating a document")

    assignments.append("updated_at = NOW()")
    params.append(document_id)



    _run_write(
        f"""
        UPDATE documents
        SET {", ".join(assignments)}
        WHERE id = %s
        """,
        params,
    )
