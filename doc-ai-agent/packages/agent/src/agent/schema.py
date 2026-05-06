from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FetchGroupReadmeRequest(BaseModel):
    """
    Schema for the input to the fetch_group_readme tool.
    """
    group_name: str = Field(..., description="The name of the GitHub group to fetch the README for.")

class FetchGroupReadmeResponse(BaseModel):
    """
    Schema for the output from the fetch_group_readme tool.
    """
    group_name: str = Field(..., description="The name of the GitHub group.")
    readme_content: str = Field(..., description="The content of the README file for the specified GitHub group.")


# Vector Search Tools
class VectorSearchByGroupRequest(BaseModel):
    """Search documents in a group using vector similarity."""
    group_id: str = Field(..., description="The ID of the group to search within")
    embedding: List[float] = Field(..., description="The embedding vector (768-dimensional)")
    limit: int = Field(default=10, description="Maximum number of results to return")
    min_similarity: Optional[float] = Field(default=0.6, description="Minimum similarity threshold (0-1)")

class SearchResult(BaseModel):
    """A document search result."""
    document_id: str = Field(..., description="The document ID")
    path: Optional[str] = Field(..., description="Document path")
    similarity: float = Field(..., description="Similarity score (0-1)")
    content_preview: Optional[str] = Field(..., description="First 200 characters of content")

class VectorSearchByGroupResponse(BaseModel):
    """Response from vector search in a group."""
    group_id: str
    results: List[SearchResult]
    total_found: int


# Summary Generation Tools
class GenerateSummaryRequest(BaseModel):
    """Generate a summary of document or group content."""
    content: str = Field(..., description="The content to summarize")
    max_length: int = Field(default=500, description="Maximum length of summary in words")
    focus: Optional[str] = Field(default=None, description="Focus area for summary (e.g., 'key_points', 'architecture', 'team')")

class GenerateSummaryResponse(BaseModel):
    """Response with generated summary."""
    original_length: int
    summary: str
    summary_length: int


# CRUD Tools
class CreateDocumentRequest(BaseModel):
    """Create a new document in the system."""
    document_id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    source: str = Field(..., description="Source of the document (e.g., 'github', 'jira')")
    path: Optional[str] = Field(default=None, description="Document path")
    group_id: Optional[str] = Field(default=None, description="Group ID to assign to")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class CreateDocumentResponse(BaseModel):
    """Response from document creation."""
    document_id: str
    status: str  # "created"
    group_id: Optional[str]


class ReadDocumentRequest(BaseModel):
    """Read/retrieve a document."""
    document_id: str = Field(..., description="The document ID to retrieve")

class DocumentDetails(BaseModel):
    """Full document details."""
    document_id: str
    title: Optional[str]
    content: str
    source: str
    path: Optional[str]
    group_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]

class ReadDocumentResponse(BaseModel):
    """Response from reading a document."""
    document: DocumentDetails


class UpdateDocumentRequest(BaseModel):
    """Update an existing document."""
    document_id: str = Field(..., description="The document ID to update")
    title: Optional[str] = Field(default=None, description="New title")
    content: Optional[str] = Field(default=None, description="New content")
    path: Optional[str] = Field(default=None, description="New path")
    group_id: Optional[str] = Field(default=None, description="New group ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Updated metadata")

class UpdateDocumentResponse(BaseModel):
    """Response from document update."""
    document_id: str
    status: str  # "updated"
    updated_fields: List[str]


# Action Tools
class AssignDocumentRequest(BaseModel):
    """Assign a document to a group."""
    document_id: str = Field(..., description="The document ID")
    group_id: str = Field(..., description="The group ID to assign to")
    confidence: float = Field(default=0.8, description="Confidence score (0-1)")
    reason: str = Field(..., description="Reason for assignment")

class AssignDocumentResponse(BaseModel):
    """Response from document assignment."""
    document_id: str
    group_id: str
    status: str  # "assigned"
    previous_group_id: Optional[str]


class CreateGroupRequest(BaseModel):
    """Create a new document group."""
    group_id: str = Field(..., description="Unique identifier for the group")
    name: str = Field(..., description="Human-readable name for the group")
    description: Optional[str] = Field(default=None, description="Group description")
    initial_documents: Optional[List[str]] = Field(default=None, description="Initial document IDs to add")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Group metadata")

class CreateGroupResponse(BaseModel):
    """Response from group creation."""
    group_id: str
    name: str
    status: str  # "created"
    document_count: int


class HumanReviewRequest(BaseModel):
    """Flag a document for human review."""
    document_id: str = Field(..., description="The document ID to flag")
    reason: str = Field(..., description="Reason for human review")
    suggested_group_id: Optional[str] = Field(default=None, description="Suggested group ID")
    priority: str = Field(default="medium", description="Priority level: low, medium, high")
    assigned_to: Optional[str] = Field(default=None, description="User to assign for review")

class HumanReviewResponse(BaseModel):
    """Response from human review flag."""
    document_id: str
    status: str  # "flagged_for_review"
    review_id: str
    priority: str


