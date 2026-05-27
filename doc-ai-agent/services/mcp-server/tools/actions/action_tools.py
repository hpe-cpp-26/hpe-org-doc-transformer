from fastmcp import FastMCP
import logging
import uuid
from typing import Any

from agent.schema import (
    AssignDocumentRequest,
    AssignDocumentResponse,
    CreateGroupRequest,
    CreateGroupResponse,
    HumanReviewRequest,
    HumanReviewResponse,
)

logger = logging.getLogger(__name__)


def register_action_tools(mcp: FastMCP):
    """Register action tools: assign, create_group, human_review."""

    @mcp.tool
    async def assign_document(request: AssignDocumentRequest) -> AssignDocumentResponse:
        """
        Assign a document to a group.
        
        Assigns or reassigns a document to a specific group, recording
        the confidence score and reason for the assignment.
        
        Args:
            request.document_id: The document to assign
            request.group_id: The target group
            request.confidence: Confidence score (0-1)
            request.reason: Reason for assignment
            
        Returns:
            Confirmation with previous group (if reassignment)
        """
        from db.connection import get_connection

        doc_id = request.document_id
        group_id = request.group_id
        confidence = request.confidence
        reason = request.reason

        logger.info(
            "Assigning document %s to group %s (confidence: %.2f)",
            doc_id,
            group_id,
            confidence,
        )

        try:
            with get_connection() as connection:
                with connection.transaction():
                    with connection.cursor() as cursor:
                        # Get previous group ID
                        cursor.execute(
                            "SELECT group_id FROM documents WHERE id = %s",
                            [doc_id],
                        )
                        row = cursor.fetchone()
                        previous_group_id = row["group_id"] if row else None

                        # Update document assignment
                        cursor.execute(
                            """
                            UPDATE documents
                            SET group_id = %s, updated_at = NOW()
                            WHERE id = %s
                            """,
                            [group_id, doc_id],
                        )

                        # Log assignment action
                        cursor.execute(
                            """
                            INSERT INTO document_assignments 
                            (document_id, group_id, confidence, reason, assigned_at)
                            VALUES (%s, %s, %s, %s, NOW())
                            """,
                            [doc_id, group_id, confidence, reason],
                        )

            logger.info(
                "Document %s assigned to group %s (was in %s)",
                doc_id,
                group_id,
                previous_group_id,
            )

            return AssignDocumentResponse(
                document_id=doc_id,
                group_id=group_id,
                status="assigned",
                previous_group_id=previous_group_id,
            )

        except Exception as exc:
            logger.error("Failed to assign document %s: %s", doc_id, exc)
            raise

    @mcp.tool
    async def create_group(request: CreateGroupRequest) -> CreateGroupResponse:
        """
        Create a new document group.
        
        Creates a new group for organizing documents. Optionally initializes
        the group with a set of documents and generates initial centroid.
        
        Args:
            request.group_id: Unique group identifier
            request.name: Human-readable group name
            request.description: Optional group description
            request.initial_documents: Optional list of document IDs to add
            request.metadata: Optional group metadata
            
        Returns:
            Confirmation with group details
        """
        from db.connection import get_connection
        from db.vector_queries import update_centroid
        import numpy as np

        group_id = request.group_id
        name = request.name
        description = request.description or ""
        initial_documents = request.initial_documents or []

        logger.info(
            "Creating group: %s (name: %s, initial docs: %d)",
            group_id,
            name,
            len(initial_documents),
        )

        try:
            with get_connection() as connection:
                with connection.transaction():
                    with connection.cursor() as cursor:
                        # Create the group
                        cursor.execute(
                            """
                            INSERT INTO groups (id, name, description, metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, NOW(), NOW())
                            ON CONFLICT (id) DO UPDATE SET
                                name = EXCLUDED.name,
                                description = EXCLUDED.description,
                                metadata = EXCLUDED.metadata,
                                updated_at = NOW()
                            """,
                            [group_id, name, description, request.metadata],
                        )

                        # Assign initial documents
                        if initial_documents:
                            for doc_id in initial_documents:
                                cursor.execute(
                                    """
                                    UPDATE documents
                                    SET group_id = %s, updated_at = NOW()
                                    WHERE id = %s
                                    """,
                                    [group_id, doc_id],
                                )

                            # Calculate and update centroid
                            cursor.execute(
                                """
                                SELECT embedding FROM documents
                                WHERE group_id = %s AND embedding IS NOT NULL
                                """,
                                [group_id],
                            )
                            rows = cursor.fetchall()

                            if rows:
                                embeddings = [row["embedding"] for row in rows]
                                # Convert embeddings to numpy arrays for averaging
                                embeddings_array = np.array([list(e) for e in embeddings])
                                centroid = np.mean(embeddings_array, axis=0).tolist()

                                # Update group centroid
                                centroid_literal = "[" + ",".join(str(float(v)) for v in centroid) + "]"
                                cursor.execute(
                                    """
                                    UPDATE groups
                                    SET centroid = %s::vector, doc_count = %s, updated_at = NOW()
                                    WHERE id = %s
                                    """,
                                    [centroid_literal, len(rows), group_id],
                                )

            logger.info(
                "Group created: %s with %d documents",
                group_id,
                len(initial_documents),
            )

            return CreateGroupResponse(
                group_id=group_id,
                name=name,
                status="created",
                document_count=len(initial_documents),
            )

        except Exception as exc:
            logger.error("Failed to create group %s: %s", group_id, exc)
            raise

    @mcp.tool
    async def flag_for_human_review(
        request: HumanReviewRequest,
    ) -> HumanReviewResponse:
        """
        Flag a document for human review.
        
        Creates a review task for human inspection when automated classification
        is uncertain or needs validation. Optionally suggests a group assignment.
        
        Args:
            request.document_id: Document to review
            request.reason: Reason for review request
            request.suggested_group_id: Optional suggested group
            request.priority: Priority level (low/medium/high)
            request.assigned_to: Optional reviewer assignment
            
        Returns:
            Confirmation with review_id for tracking
        """
        from db.connection import get_connection

        doc_id = request.document_id
        reason = request.reason
        priority = request.priority
        review_id = str(uuid.uuid4())

        logger.info(
            "Flagging document %s for human review (priority: %s, reason: %s)",
            doc_id,
            priority,
            reason,
        )

        try:
            with get_connection() as connection:
                with connection.transaction():
                    with connection.cursor() as cursor:
                        # Create review record
                        cursor.execute(
                            """
                            INSERT INTO document_reviews 
                            (id, document_id, suggested_group_id, reason, priority, 
                             assigned_to, status, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                            """,
                            [
                                review_id,
                                doc_id,
                                request.suggested_group_id,
                                reason,
                                priority,
                                request.assigned_to,
                                "pending",
                            ],
                        )

                        # Update document status
                        cursor.execute(
                            """
                            UPDATE documents
                            SET review_status = %s, review_id = %s, updated_at = NOW()
                            WHERE id = %s
                            """,
                            ["pending_review", review_id, doc_id],
                        )

            logger.info(
                "Document %s flagged for human review with ID: %s",
                doc_id,
                review_id,
            )

            return HumanReviewResponse(
                document_id=doc_id,
                status="flagged_for_review",
                review_id=review_id,
                priority=priority,
            )

        except Exception as exc:
            logger.error("Failed to flag document %s for review: %s", doc_id, exc)
            raise
