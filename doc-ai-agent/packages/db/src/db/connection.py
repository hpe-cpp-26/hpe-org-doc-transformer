from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row


class DatabaseConnectionError(RuntimeError):
    """Raised when PostgreSQL cannot be reached or a connection becomes unusable."""


_connection: Connection[Any] | None = None


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/doc_ai",
    )


def _open_connection() -> Connection[Any]:
    try:
        return psycopg.connect(get_database_url(), row_factory=dict_row)
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Unable to connect to PostgreSQL") from exc


def _get_or_create_connection() -> Connection[Any]:
    global _connection

    if _connection is None or _connection.closed:
        _connection = _open_connection()
    return _connection


def close_connection() -> None:
    global _connection

    if _connection is not None and not _connection.closed:
        _connection.close()
    _connection = None


@contextmanager
def get_connection() -> Iterator[Connection[Any]]:
    connection = _get_or_create_connection()
    try:
        yield connection
    except psycopg.Error as exc:
        close_connection()
        raise DatabaseConnectionError("Database operation failed") from exc