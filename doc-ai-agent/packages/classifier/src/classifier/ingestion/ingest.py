from __future__ import annotations
import logging
from typing import Any
from classifier.ingestion.prototypes import assign_group
from db import  write_to_db


logger = logging.getLogger(__name__)

DOC_PREFIX = "search_document: "


def ingest_document(
    doc_id: str,
    doc_path: str | None,
    group_id: str | None,
    content: str,
    doc_info: dict[str, Any] | None = None,
    chunks: list[dict[str, Any]] | None = None,
    segments: list[dict[str, Any]] | None = None,
    conn: Any | None = None,
) -> dict[str, Any]:
    

    segment_count = len(segments)
    total_chunks = len(chunks)

    
    write_to_db(
            conn,
            doc_id,
            doc_path,
            group_id,
            content,
            segment_count,
            total_chunks,
            chunks,
            segments,
        )
    assign_group(doc_id, group_id, segments, conn=conn)
    
    logger.info("ingest_document: document ingested successfully (doc_id=%s)", doc_id)
    logger.info("ingest_document: document assigned to group_id=%s", group_id)
    
    return {
        "doc_id": doc_id,
        "doc_path": doc_path,
        "content": content,
        "doc_info": doc_info,
        "chunks": chunks,
        "segments": segments,
        "n_chunks": len(chunks),
        "n_segments": len(segments),
    }

