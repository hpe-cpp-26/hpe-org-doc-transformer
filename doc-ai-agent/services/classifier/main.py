"""Classifier service - categorize documents into groups."""

import logging

from classifier import DocumentClassifier
from config import configure_logging, get_settings
from doc_types.documents import NormalisedDocument


def main() -> None:
    settings = get_settings(service_name="classifier")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Classifier service starting")

    example_doc = NormalisedDocument(
        id="github-db-guide-789",
        source="github",
        title="Database Optimization Guide",
        content="""Database Optimization Guide

Best practices for optimizing your database queries.

Query Performance

Use indexes on frequently queried columns.
Avoid SELECT *, instead specify columns you need.
Consider query execution plans.
""",
        path="docs/database-guide.md",
    )

    logger.info("Classifying example document", extra={"doc_id": example_doc.id})

    try:
        result = DocumentClassifier.classify(example_doc)
    except ConnectionError as exc:
        logger.error("Classification failed", exc_info=exc)
        return

    print("=" * 64)
    print("CLASSIFIER SERVICE")
    print("=" * 64)
    print("Document")
    print(f"  ID: {example_doc.id}")
    print(f"  Title: {example_doc.title}")
    print(f"  Source: {example_doc.source}")
    print(f"  Content length: {len(example_doc.content)} chars")
    print()
    print("Classification Result")
    print(f"  Action: {result.action}")
    print(f"  Group ID: {result.group_id}")
    print(f"  Similarity Score: {result.similarity_score}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reason: {result.reason}")


if __name__ == "__main__":
    main()
