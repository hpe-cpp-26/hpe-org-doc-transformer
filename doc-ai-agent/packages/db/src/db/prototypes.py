from typing import Any

from .utils import parse_embedding, _vector_literal


def delete_proto_buffer(doc_id: str, conn: Any) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM prototype_buffer WHERE doc_id = %s",
            [doc_id],
        )


def insert_into_proto_buffer(
    group_id: str,
    doc_id: str,
    segments: list[dict[str, Any]],
    conn: Any,
) -> None:
    with conn.cursor() as cursor:
        for segment in segments:
            embedding = parse_embedding(segment.get("embedding"))
            cursor.execute(
                """
                INSERT INTO prototype_buffer
                    (group_id, doc_id, segment_index, embedding)
                VALUES (%s, %s, %s, %s::vector)
                """,
                [
                    group_id,
                    doc_id,
                    segment["segment_index"],
                    _vector_literal(embedding),
                ],
            )
                    
def refresh_buffer_for_doc(
    doc_id: str,
    group_id: str,
    segments: list[dict[str, Any]],
    conn: Any,
) -> None:
    delete_proto_buffer(doc_id, conn)
    insert_into_proto_buffer(group_id, doc_id, segments, conn)


def refresh_doc_count(group_id: str, conn: Any) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE groups
            SET doc_count = (
                SELECT COUNT(*) FROM documents WHERE group_id = %s
            ),
            updated_at = NOW()
            WHERE id = %s
            """,
            [group_id, group_id],
        )


def count_buffered(group_id: str, conn: Any) -> int:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM prototype_buffer WHERE group_id = %s",
            [group_id],
        )
        row = cursor.fetchone()
        return int(row.get("total") or 0)


def fetch_buffer_embeddings(group_id: str, conn: Any) -> list[list[float]]:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT embedding FROM prototype_buffer WHERE group_id = %s",
            [group_id],
        )
        rows = cursor.fetchall()
    return [parse_embedding(row.get("embedding")) for row in rows]


def upsert_prototypes(
    group_id: str,
    prototypes: list[list[float]],
    conn: Any,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM group_prototypes WHERE group_id = %s",
            [group_id],
        )
        for idx, proto in enumerate(prototypes):
            cursor.execute(
                """
                INSERT INTO group_prototypes
                    (group_id, proto_index, embedding)
                VALUES (%s, %s, %s::vector)
                ON CONFLICT (group_id, proto_index) DO UPDATE SET
                    embedding  = EXCLUDED.embedding,
                    created_at = NOW()
                """,
                [group_id, idx, _vector_literal(proto)],
            )

def clear_buffer(group_id: str, conn: Any) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM prototype_buffer WHERE group_id = %s",
            [group_id],
        )

def update_proto_count(group_id:str, count: int, conn: Any) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE groups
            SET proto_count= %s,
            updated_at = NOW()
            WHERE id = %s
            """,
            [count, group_id],
        )