import logging

from config import configure_logging, get_settings


def main() -> None:
    settings = get_settings(service_name="classifier")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Classifier Service starting")
"""Classifier service - Categorize documents into groups."""

from classifier import DocumentClassifier, ClassificationResult
from doc_types.documents import NormalisedDocument


def main():
    """Example usage of the document classifier."""
    
    # Example: Create a normalized document
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
    
    print("=" * 60)
    print("CLASSIFIER SERVICE EXAMPLE")
    print("=" * 60)
    print()
    
    print("Step 1: Normalized Document")
    print(f"  ID: {example_doc.id}")
    print(f"  Title: {example_doc.title}")
    print(f"  Source: {example_doc.source}")
    print(f"  Content length: {len(example_doc.content)} chars")
    print()
    
    # Classify the document
    print("Step 2: Classifying Document...")
    print("  - Generating 768-dim embedding...")
    print("  - Searching similar group centroids...")
    print("  - Applying thresholds...")
    print()
    
    try:
        result = DocumentClassifier.classify(example_doc)
        
        print("Step 3: Classification Result")
        print(f"  Document ID: {result.document_id}")
        print(f"  Action: {result.action}")
        print(f"  Group ID: {result.group_id}")
        print(f"  Similarity Score: {result.similarity_score}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reason: {result.reason}")
        print()
        
        # Explain thresholds / routing
        print("Threshold Routing Logic:")
        print("  > 0.80 → AUTO_ASSIGN to existing group and update README/index.json via GitHub")
        print("  0.40-0.80 → ROUTE_TO_AGENT for LLM + tool inspection")
        print("  < 0.40 → CREATE_NEW_GROUP or FLAG_FOR_REVIEW (human) ")
        
    except ConnectionError as e:
        print(f"ERROR: {e}")
        print()
        print("Setup required:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Pull model: ollama pull nomic-embed-text")
        print("  3. Start PostgreSQL: docker-compose up -d")


if __name__ == "__main__":
    main()
