from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseConnectionError(RuntimeError):
    """Raised when PostgreSQL cannot be reached or a connection becomes unusable."""


_pool: ConnectionPool | None = None
_autocommit_pool: ConnectionPool | None = None


def get_database_url() -> str:
   url = os.getenv("DATABASE_URL")
   
   if not url:
       raise ValueError(
           "DATABASE_URL  not configured"
       )
   return url


def _get_pool(autocommit: bool = False) -> ConnectionPool:
    global _pool, _autocommit_pool

    if autocommit:
        if _autocommit_pool is None:
            _autocommit_pool = ConnectionPool(
                conninfo=get_database_url(),
                kwargs={
                    "row_factory": dict_row,
                    "autocommit": True,
                },
                min_size=2,
                max_size=10,
                open=True,
            )
        return _autocommit_pool
    else:
        if _pool is None:
            _pool = ConnectionPool(
                conninfo=get_database_url(),
                kwargs={
                    "row_factory": dict_row,
                },
                min_size=2,
                max_size=10,
                open=True,
            )
        return _pool


def close_pools() -> None:
    global _pool, _autocommit_pool

    for pool in (_pool, _autocommit_pool):
        if pool is not None:
            pool.close()

    _pool = None
    _autocommit_pool = None


@contextmanager
def get_connection(autocommit: bool = False) -> Iterator[Connection[Any]]:
    pool = _get_pool(autocommit=autocommit)

    try:
        with pool.connection() as conn:
            yield conn
    except psycopg.Error as exc:
        raise DatabaseConnectionError("Database operation failed") from exc