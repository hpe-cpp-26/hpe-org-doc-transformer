"""Duplicate document detection before vector search."""

import logging

from db.connection import DatabaseConnectionError
from db.vector_queries import get_document_assignment
from types import ClassificationResult, NormalisedDocument


def check_duplicate_assignment(
    normalized_doc: NormalisedDocument,
) -> ClassificationResult | None:
    logger = logging.getLogger(__name__)
    doc_id = normalized_doc.id

    if not doc_id:
        return None

    try:
        existing_group_id, existing_path = get_document_assignment(doc_id)
    except DatabaseConnectionError as exc:
        logger.warning(
            "Failed to check existing document; proceeding with vector search",
            extra={"doc_id": doc_id},
            exc_info=exc,
        )
        return None

    if not existing_group_id:
        return None

    logger.info(
        "Duplicate document detected; assigned to existing group",
        extra={"doc_id": doc_id, "group_id": existing_group_id},
    )
    return ClassificationResult(
        document_id=doc_id,
        action="AUTO_ASSIGN",
        group_id=existing_group_id,
        path=existing_path,
        similarity_score=None,
        confidence=1.0,
        reason=f"Duplicate doc_id assigned to existing group '{existing_group_id}'",
    )
