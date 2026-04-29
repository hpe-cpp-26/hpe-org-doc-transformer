"""Document classification using embeddings and centroid search."""

from typing import Optional

from embedding import generate_embedding
from db.vector_queries import search_similar_centroid
from types import NormalisedDocument, ClassificationResult

from .actions import github_update_readme_and_index, route_to_agent, flag_for_human_review


class DocumentClassifier:
    """Classifies normalized documents into groups using embeddings and centroid search."""
    
    # Thresholds for classification decisions
    AUTO_ASSIGN_THRESHOLD = 0.80
    # If similarity is > AGENT_ROUTE_THRESHOLD and <= AUTO_ASSIGN_THRESHOLD,
    # route to the Agent for further inspection (LLM + tools).
    AGENT_ROUTE_THRESHOLD = 0.40
    
    @staticmethod
    def classify(
        normalized_doc: NormalisedDocument,
        top_k: int = 10,
    ) -> ClassificationResult:
        """
        Classify a normalized document.
        
          Algorithm:
          1. Generate 768-dim embedding from normalized content
          2. Search for similar group centroids (cosine similarity)
          3. Apply threshold routing:
              - similarity >= 0.80 → AUTO_ASSIGN to that group
              - 0.40 <= similarity < 0.80 → ROUTE_TO_AGENT (Agent inspects candidates)
              - similarity < 0.40 → CREATE_NEW_GROUP or FLAG_FOR_REVIEW
        
        Args:
            normalized_doc: The normalized document to classify
            top_k: Number of similar groups to consider (default: 10)
            
        Returns:
            ClassificationResult with action and confidence
            
        Raises:
            ConnectionError: If embedding generation fails
        """
        
        # Step 1: Generate 768-dimensional embedding
        embedding = generate_embedding(normalized_doc.content)
        
        # Step 2: Search for similar group centroids
        similar_groups = search_similar_centroid(
            embedding,
            limit=top_k,
            min_similarity=DocumentClassifier.AGENT_ROUTE_THRESHOLD,
        )
        
        # Step 3: Apply threshold routing logic
        if not similar_groups:
            # No groups found at all → low confidence
            flag_for_human_review(normalized_doc.id, "no similar groups found")
            return ClassificationResult(
                document_id=normalized_doc.id,
                action="CREATE_NEW_GROUP",
                group_id=None,
                similarity_score=None,
                confidence=0.0,
                reason="No similar groups found (below route threshold)",
            )

        # Get top result
        top_group = similar_groups[0]
        similarity = top_group["similarity"]

        if similarity >= DocumentClassifier.AUTO_ASSIGN_THRESHOLD:
            # High confidence: auto-assign and trigger GitHub updates
            github_update_readme_and_index(normalized_doc.id, top_group["id"])
            return ClassificationResult(
                document_id=normalized_doc.id,
                action="AUTO_ASSIGN",
                group_id=top_group["id"],
                similarity_score=similarity,
                confidence=similarity,
                reason=f"High similarity ({similarity:.2f}) to group '{top_group['name']}'",
            )

        if similarity >= DocumentClassifier.AGENT_ROUTE_THRESHOLD:
            # Ambiguous: route to Agent for deeper inspection
            route_to_agent(normalized_doc, similar_groups)
            return ClassificationResult(
                document_id=normalized_doc.id,
                action="ROUTE_TO_AGENT",
                group_id=top_group["id"],
                similarity_score=similarity,
                confidence=similarity,
                reason=f"Ambiguous similarity ({similarity:.2f}) - routed to Agent",
            )

        # Low confidence: flag or create new group
        flag_for_human_review(normalized_doc.id, f"low similarity {similarity:.2f}")
        return ClassificationResult(
            document_id=normalized_doc.id,
            action="CREATE_NEW_GROUP",
            group_id=None,
            similarity_score=similarity,
            confidence=0.0,
            reason=f"Low similarity ({similarity:.2f}) - creating new group or flagging for review",
        )
