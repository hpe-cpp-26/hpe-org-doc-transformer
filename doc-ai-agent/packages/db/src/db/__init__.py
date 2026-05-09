from .connection import close_connection, get_connection, get_database_url
from .vector_queries import (
    insert_chunks,
    insert_document,
    search_similar_centroid,
    update_centroid,
    update_document,
)

"""
The __all__ variable defines the public API of this package. 
It specifies which names are intended to be accessible 
when someone imports * from this module. By listing these names, 
we make it clear which functions are meant to be used by external code,
and we can also prevent accidental access to internal functions or
variables that are not part of the public interface.
"""

__all__ = [
    "close_connection",
    "get_connection",
    "get_database_url",
    "insert_chunks",
    "insert_document",
    "search_similar_centroid",
    "update_centroid",
    "update_document",
]