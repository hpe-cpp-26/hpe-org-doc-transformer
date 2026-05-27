from db.utils import Vector, _run_write, _vector_literal
from db.connection import get_connection, DatabaseConnectionError
from doc_types.documents import DocumentAssignment
import psycopg
from typing import Any
import ast



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


def get_document_assignment(document_id: str) -> DocumentAssignment:
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

    # pgvector returns the embedding column as a raw string '[0.1,0.2,...]'.
    # Parse it into list[float] so Pydantic validation passes.
    raw_embedding = row.get("embedding")
    if isinstance(raw_embedding, str):
        raw_embedding = ast.literal_eval(raw_embedding)
    if raw_embedding is not None:
        raw_embedding = [float(v) for v in raw_embedding]

    return DocumentAssignment(
        group_id=row.get("group_id"),
        embedding=raw_embedding,
        path=row.get("path"),
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



    _run_write(
        f"""
        UPDATE documents
        SET {", ".join(assignments)}
        WHERE id = %s
        """,
        params,
    )
