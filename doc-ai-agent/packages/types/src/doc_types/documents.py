from typing import Optional
from pydantic import BaseModel


class NormalisedDocument(BaseModel):
    """Represents a standardized document after normalization."""
    doc_id: str
    source: str
    title: Optional[str]
    content: str
    metadata: dict

class ClassificationResult(BaseModel):
    """Result from document classification."""
    document_id: str
    action: str  # "AUTO_ASSIGN", "REVIEW_BY_AGENT", "CREATE_NEW_GROUP"
    group_id: Optional[str] = None
    path: Optional[str] = None
    similarity_score: Optional[float] = None
    confidence: float
    reason: str

class DocumentAssignment(BaseModel):
    """Represents the assignment of a document to a group."""
    group_id: Optional[str] = None
    embedding: Optional[list[float]] = None
    path: Optional[str] = None
    
