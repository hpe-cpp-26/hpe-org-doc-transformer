from db.utils import Vector, _vector_literal, _run_write
from db.connection import get_connection, DatabaseConnectionError
import psycopg
import ast


def insert_doc_embedding_cache(
    doc_id: str,
    embedding: Vector,
) -> None:
    
    query = """
        INSERT INTO doc_embedding_cache (doc_id, embedding)
        VALUES (%s, %s::vector)
        ON CONFLICT (doc_id) DO UPDATE SET
            embedding = EXCLUDED.embedding
    """
    _run_write(query, [doc_id, _vector_literal(embedding)])
    

def fetch_embedding_from_cache(doc_id:str) -> Vector | None:
    query = "SELECT embedding FROM doc_embedding_cache WHERE doc_id = %s"

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, [doc_id])
                row = cursor.fetchone()
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Document embedding cache lookup failed") from exc

    if not row:
        return None

    embedding = row.get("embedding")
    if isinstance(embedding, str):
        embedding = ast.literal_eval(embedding)

    return [float(v) for v in embedding]
