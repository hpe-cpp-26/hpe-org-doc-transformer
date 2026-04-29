from typing import Optional
from pydantic import BaseModel

class NormalisedDocument(BaseModel):
    """Represents a standardized document after normalization."""
    id: str
    source: str  # "github" or "jira"
    title: str
    content: str
    path: Optional[str] = None
    group_id: Optional[str] = None
    metadata: dict = {}


class ClassificationResult(BaseModel):
    """Result from document classification."""
    document_id: str
    action: str  # "AUTO_ASSIGN", "REVIEW_BY_AGENT", "CREATE_NEW_GROUP"
    group_id: Optional[str] = None
    similarity_score: Optional[float] = None
    confidence: float
    reason: str
