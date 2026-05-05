from typing import Literal, TypedDict, Optional

class ClassifierState(TypedDict):
    """Normalised input data"""
    doc_id: str
    source: str
    title: Optional[str]
    content: str
    metadata: dict
    
    """Optional fingerprint field that holds data that can be used for efficient matching."""
    fingerprint: Optional[str]
    
    """validation check"""
    is_valid: Optional[bool] 

    """Duplication Check"""
    is_duplicate:bool
    existing_group_id: Optional[str]

    """Embedding"""
    embedding: Optional[list[float]]

    """Group centroid search"""
    similar_group_candidates: Optional[list[dict]]
    top_similarity_score: Optional[float]

    """classification result"""
    classification_route: Optional[Literal["AUTO_ASSIGN", "REVIEW_BY_AGENT", "CREATE_NEW_GROUP"]]

    """Agent context and decision making"""
    agent_context: Optional[dict]
    group_readmes: Optional[dict]
    sources_content_from_mcp: Optional[dict]
    agent_decision: Optional[dict]

    """Final Decision"""
    assinged_group_id: Optional[str]
    create_new_group: Optional[bool]
    github_write_status: Optional[str]
    db_update_status: Optional[str]
    readme_update_status: Optional[str] 


    """Audit and error handling"""
    decision_path: Optional[str]
    errors: Optional[list[str]]


