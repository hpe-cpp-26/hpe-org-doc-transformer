from app.db.chunks import search_similar_chunks
from app.services.embedding_service import generate_embedding
from app.services.reranking_service import rerank_chunks

def retrieve_chunks(
    query: str,
    limit: int=10,
):
    embedding = generate_embedding(query)
    
    initial_chunks = search_similar_chunks(
        embedding=embedding,
        limit=50 
    )
    
    reranked_chunks = rerank_chunks(
        query=query,
        chunks=initial_chunks,
        top_k=limit
    )
    
    return reranked_chunks