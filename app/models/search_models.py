from pydantic import BaseModel

class Source(BaseModel):
    doc_id: str
    doc_path: str
    url: str
    chunk_text: str
    similarity: float

class SearchRequest(BaseModel):
    query:str
    
class SearchResponse(BaseModel):
    answer: str
    confidence_score: float
    sources: list[Source]