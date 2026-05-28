from .connection import  get_connection, get_database_url
from .documents import insert_document, get_document_assignment, update_document
from .groups import  search_similar_prototypes, insert_new_group, search_similar_buffer, search_similar_segments
from .chunks import insert_chunks, search_similar_chunks_by_group
from .cache import insert_doc_embedding_cache, fetch_embedding_from_cache
from .ingestion import write_to_db
from .prototypes import refresh_buffer_for_doc, refresh_doc_count, count_buffered, fetch_buffer_embeddings

"""
The __all__ variable defines the public API of this package. 
"""

__all__ = [
    "get_connection",
    "get_database_url",
    "insert_chunks",
    "insert_document",
    "search_similar_centroid",
    "search_similar_prototypes",
    "update_centroid",
    "update_document",
    "insert_doc_embedding_cache",
    "fetch_embedding_from_cache",
    "search_similar_chunks_by_group",
    "get_document_assignment",
    "insert_new_group",
    "write_to_db",
    "insert_into_proto_buffer",
    "delete_proto_buffer",
    "refresh_buffer_for_doc",
    "refresh_doc_count",
    "count_buffered",
    "fetch_buffer_embeddings",
    "search_similar_buffer",
    "search_similar_segments"
]

