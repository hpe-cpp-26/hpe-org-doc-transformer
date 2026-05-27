from collections.abc import Sequence
from typing import Any
import psycopg
from .connection import DatabaseConnectionError, get_connection

Vector = Sequence[float | int]

def _vector_literal(values: Vector) -> str:
    if not values:
        raise ValueError("Embedding vectors cannot be empty")
    return "[" + ",".join(str(float(v)) for v in values) + "]"

def _run_write(query: str, params: Sequence[Any]) -> None:
    try:
        with get_connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Database write failed") from exc