from fastmcp import FastMCP
import logging
from typing import Any, Optional
import psycopg

from agent.schema import (
    CreateDocumentRequest,
    CreateDocumentResponse,
    ReadDocumentRequest,
    ReadDocumentResponse,
    DocumentDetails,
    UpdateDocumentRequest,
    UpdateDocumentResponse,
)

logger = logging.getLogger(__name__)


def register_crud_tools(mcp: FastMCP):
    """Register CRUD (Create, Read, Update) tools for documents."""

    @mcp.tool
    async def create_document(request: CreateDocumentRequest) -> CreateDocumentResponse:
        """
        Create a new document in the system.
        
        Stores document content with metadata. If group_id is provided,
        the document is assigned to that group. The document will be
        indexed for vector similarity search.
        
        Args:
            request.document_id: Unique identifier
            request.title: Document title
            request.content: Document content
            request.source: Source (github, jira, etc.)
            request.path: Optional document path
            request.group_id: Optional group assignment
            request.metadata: Optional metadata dict
            
        Returns:
            Confirmation with document_id and assigned group_id
        """
        from db.connection import get_connection
        from embedding.embedder import Embedder

        doc_id = request.document_id
        content = request.content
        group_id = request.group_id

        logger.info("Creating document: %s (source: %s, group: %s)", doc_id, request.source, group_id)

        try:
            # Generate embedding for the document
            embedder = Embedder()
            embedding = embedder.embed(content)

            # Insert document into database
            with get_connection() as connection:
                with connection.transaction():
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO documents 
                            (id, path, group_id, content, embedding, source, title, metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s::vector, %s, %s, %s, NOW(), NOW())
                            ON CONFLICT (id) DO UPDATE SET
                                path = EXCLUDED.path,
                                group_id = EXCLUDED.group_id,
                                content = EXCLUDED.content,
                                embedding = EXCLUDED.embedding,
                                source = EXCLUDED.source,
                                title = EXCLUDED.title,
                                metadata = EXCLUDED.metadata,
                                updated_at = NOW()
                            """,
                            [
                                doc_id,
                                request.path,
                                group_id,
                                content,
                                "[" + ",".join(str(float(v)) for v in embedding) + "]",
                                request.source,
                                request.title,
                                request.metadata,
                            ],
                        )

            logger.info("Document created successfully: %s", doc_id)

            return CreateDocumentResponse(
                document_id=doc_id,
                status="created",
                group_id=group_id,
            )

        except Exception as exc:
            logger.error("Failed to create document %s: %s", doc_id, exc)
            raise

    @mcp.tool
    async def read_document(request: ReadDocumentRequest) -> ReadDocumentResponse:
        """
        Read/retrieve a document from the system.
        
        Retrieves all stored information about a document including
        content, metadata, and group assignment.
        
        Args:
            request.document_id: The document ID to retrieve
            
        Returns:
            Complete document details
        """
        from db.connection import get_connection

        doc_id = request.document_id

        logger.info("Reading document: %s", doc_id)

        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, title, content, source, path, group_id, 
                               metadata, created_at, updated_at
                        FROM documents
                        WHERE id = %s
                        """,
                        [doc_id],
                    )
                    row = cursor.fetchone()

            if not row:
                logger.warning("Document not found: %s", doc_id)
                # Return empty document or raise error
                return ReadDocumentResponse(
                    document=DocumentDetails(
                        document_id=doc_id,
                        title=None,
                        content="",
                        source="",
                        path=None,
                        group_id=None,
                        metadata=None,
                    )
                )

            doc = DocumentDetails(
                document_id=row["id"],
                title=row["title"],
                content=row["content"],
                source=row["source"],
                path=row["path"],
                group_id=row["group_id"],
                metadata=row["metadata"],
                created_at=row["created_at"].isoformat() if row["created_at"] else None,
                updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
            )

            logger.info("Document retrieved: %s", doc_id)
            return ReadDocumentResponse(document=doc)

        except Exception as exc:
            logger.error("Failed to read document %s: %s", doc_id, exc)
            raise

    @mcp.tool
    async def update_document(request: UpdateDocumentRequest) -> UpdateDocumentResponse:
        """
        Update an existing document.
        
        Updates specified fields of a document. Only provided fields are updated.
        If content is updated, the embedding is regenerated automatically.
        
        Args:
            request.document_id: The document to update
            request.title: New title (optional)
            request.content: New content (optional, triggers re-embedding)
            request.path: New path (optional)
            request.group_id: New group assignment (optional)
            request.metadata: Updated metadata (optional)
            
        Returns:
            Confirmation with updated fields list
        """
        from db.connection import get_connection
        from embedding.embedder import Embedder

        doc_id = request.document_id

        logger.info("Updating document: %s", doc_id)

        # Collect fields to update
        assignments: list[str] = []
        params: list[Any] = []
        updated_fields: list[str] = []

        if request.title is not None:
            assignments.append("title = %s")
            params.append(request.title)
            updated_fields.append("title")

        if request.content is not None:
            # Regenerate embedding for content change
            embedder = Embedder()
            embedding = embedder.embed(request.content)
            assignments.append("content = %s")
            assignments.append("embedding = %s::vector")
            params.append(request.content)
            params.append("[" + ",".join(str(float(v)) for v in embedding) + "]")
            updated_fields.append("content")
            updated_fields.append("embedding")

        if request.path is not None:
            assignments.append("path = %s")
            params.append(request.path)
            updated_fields.append("path")

        if request.group_id is not None:
            assignments.append("group_id = %s")
            params.append(request.group_id)
            updated_fields.append("group_id")

        if request.metadata is not None:
            assignments.append("metadata = %s")
            params.append(request.metadata)
            updated_fields.append("metadata")

        if not assignments:
            logger.warning("No fields to update for document: %s", doc_id)
            return UpdateDocumentResponse(
                document_id=doc_id,
                status="updated",
                updated_fields=[],
            )

        assignments.append("updated_at = NOW()")
        params.append(doc_id)

        try:
            with get_connection() as connection:
                with connection.transaction():
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""
                            UPDATE documents
                            SET {", ".join(assignments)}
                            WHERE id = %s
                            """,
                            params,
                        )

            logger.info("Document updated: %s (fields: %s)", doc_id, ", ".join(updated_fields))

            return UpdateDocumentResponse(
                document_id=doc_id,
                status="updated",
                updated_fields=updated_fields,
            )

        except Exception as exc:
            logger.error("Failed to update document %s: %s", doc_id, exc)
            raise
