from typing import Any
from .utils import _vector_literal


def write_to_db(
    conn: Any,
    doc_id: str,
    doc_path: str | None,
    group_id: str | None,
    content: str,
    segment_count: int,
    total_chunks: int,
    chunks: list[dict[str, Any]],
    segments: list[dict[str, Any]],
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO documents (id, doc_path, group_id, content, segment_count)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                doc_path       = EXCLUDED.doc_path,
                group_id       = EXCLUDED.group_id,
                content        = EXCLUDED.content,
                segment_count  = EXCLUDED.segment_count
            """,
            [doc_id, doc_path, group_id, content, segment_count],
        )

        #document_chunks
        for chunk in chunks:
            cursor.execute(
                """
                INSERT INTO document_chunks
                    (doc_id, group_id, chunk_index, total_chunks,
                    chunk_text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s::vector)
                ON CONFLICT (doc_id, chunk_index) DO UPDATE SET
                    chunk_text   = EXCLUDED.chunk_text,
                    embedding    = EXCLUDED.embedding,
                    total_chunks = EXCLUDED.total_chunks
                """,
                [
                    doc_id,
                    group_id,
                    chunk["chunk_index"],
                    total_chunks,
                    chunk["chunk_text"],
                    _vector_literal(chunk["embedding"]),
                ],
            )

        # document_segments
        for segment in segments:
            cursor.execute(
                """
                INSERT INTO document_segments
                    (doc_id, group_id, segment_index, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (doc_id, segment_index) DO UPDATE SET
                    embedding = EXCLUDED.embedding
                """,
                [
                    doc_id,
                    group_id,
                    segment["segment_index"],
                    _vector_literal(segment["embedding"]),
                ],
            )
