import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


CROSS_ENCODER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
logger.info(f'Loading CrossEncoder model: {CROSS_ENCODER_MODEL_NAME}')
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)

def rerank_chunks(query: str, chunks: list[dict], top_k: int = 10) -> list[dict]:
    """
    Re-scores and sorts a list of chunks based on a CrossEncoder model.
    """
    if not chunks:
        return []
        
    pairs = [[query, chunk['chunk_text']] for chunk in chunks]
    
    scores = cross_encoder.predict(pairs)
    
    for chunk, score in zip(chunks, scores):
        chunk['cross_encoder_score'] = float(score)
        
    ranked_chunks = sorted(chunks, key=lambda x: x['cross_encoder_score'], reverse=True)
    return ranked_chunks[:top_k]
