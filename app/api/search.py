from fastapi import APIRouter

from app.models.search_models import (
    SearchRequest,
    SearchResponse
)

from app.services.retrieval_service import (
    retrieve_chunks
)

from app.services.llm_service import generate_answer

router = APIRouter()

def build_document_url(doc_id: str):

    if "payment-system" in doc_id:
        return "https://github.com/hpe-cpp-26/test-central-data-store/blob/main/root/payment-system-design-documentation/README.md"

    elif "self-healing-system" in doc_id:
        return "https://github.com/hpe-cpp-26/test-central-data-store/blob/main/root/self-healing-distributed-system-documentation/README.md"

    elif "travel-planner-system" in doc_id:
        return "https://github.com/hpe-cpp-26/test-central-data-store/blob/main/root/travel-planner-ai-system/README.md"

    return ""

@router.post(
    "/search",
    response_model=SearchResponse
)
def search(request: SearchRequest):
    
    chunks = retrieve_chunks(
        query=request.query,
        limit=3
    )
    
    confidence_score=0
    
    if chunks:
        confidence_score= round(
            chunks[0]["similarity"] * 100
        )
        
    for chunk in chunks:
        chunk["url"] = build_document_url(chunk["doc_id"])
    
    answer = generate_answer(
        request.query,
        chunks
    )
    
    return {
        "answer": answer,
        "confidence_score": confidence_score,
        "sources": [
            {
                "doc_id": chunk.get("doc_id", ""),
                "doc_path": chunk.get("doc_path", ""),
                "url": chunk.get("url", ""),
                "chunk_text": chunk.get("chunk_text", ""),
                "similarity": float(chunk.get("similarity", 0.0))
            }
            for chunk in chunks
        ]
    }