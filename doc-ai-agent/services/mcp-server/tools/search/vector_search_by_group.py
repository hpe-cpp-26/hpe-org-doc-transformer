from fastmcp import FastMCP
import logging
from typing import Any

from agent.schema import (
    VectorSearchByGroupRequest,
    VectorSearchByGroupResponse,
    SearchResult,
)
import psycopg

logger = logging.getLogger(__name__)


def register_vector_search_by_group_tool(mcp: FastMCP):
    """Register vector search within a specific group."""

    @mcp.tool
    async def vector_search_by_group(
        request: VectorSearchByGroupRequest,
    ) -> VectorSearchByGroupResponse:
        """
        Search for documents in a specific group using vector similarity.
        
        This searches within a group's documents using cosine similarity
        of embeddings to find the most similar documents to the provided vector.
        
        Args:
            request.group_id: The group ID to search within
            request.embedding: The embedding vector (768-dimensional)
            request.limit: Maximum number of results (default 10)
            request.min_similarity: Minimum similarity threshold 0-1 (default 0.6)
            
        Returns:
            List of matching documents with similarity scores
        """
        from db.connection import get_connection

        group_id = request.group_id
        embedding = request.embedding
        limit = request.limit
        min_similarity = request.min_similarity

        logger.info(
            "Searching for documents in group %s with %d results, min_similarity %.2f",
            group_id,
            limit,
            min_similarity,
        )

        # Convert embedding to pgvector format
        vector_literal = "[" + ",".join(str(float(v)) for v in embedding) + "]"

        query = """
            SELECT
                id,
                path,
                content,
                1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            WHERE group_id = %s
            AND embedding IS NOT NULL
        """
        params: list[Any] = [vector_literal, group_id]

        if min_similarity is not None:
            query += "\n            AND (1 - (embedding <=> %s::vector)) >= %s"
            params.extend([vector_literal, min_similarity])

        query += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([vector_literal, limit])

        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
        except psycopg.Error as exc:
            logger.error("Vector search failed: %s", exc)
            raise

        results = []
        for row in rows:
            # Truncate content for preview
            content_preview = None
            if row["content"]:
                content_preview = row["content"][:200]
                if len(row["content"]) > 200:
                    content_preview += "..."

            results.append(
                SearchResult(
                    document_id=row["id"],
                    path=row["path"],
                    similarity=float(row["similarity"]),
                    content_preview=content_preview,
                )
            )

        logger.info("Found %d documents in group %s", len(results), group_id)

        return VectorSearchByGroupResponse(
            group_id=group_id,
            results=results,
            total_found=len(results),
        )
