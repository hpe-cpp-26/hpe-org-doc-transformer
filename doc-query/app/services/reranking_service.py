import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


CROSS_ENCODER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
logger.info(f'Loading CrossEncoder model: {CROSS_ENCODER_MODEL_NAME}')
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)

import math

def rerank_chunks(query: str, chunks: list[dict], top_k: int = 10) -> list[dict]:
    """
    Re-scores and sorts a list of chunks based on a CrossEncoder model.
    Applies a sigmoid to output probabilities (0 to 1) instead of raw logits.
    """
    if not chunks:
        return []
        
    pairs = [[query, chunk['chunk_text']] for chunk in chunks]
    
    scores = cross_encoder.predict(pairs)
    
    for chunk, score in zip(chunks, scores):
        # Apply sigmoid to normalize logit to 0.0 - 1.0 probability
        sigmoid_score = 1 / (1 + math.exp(-float(score)))
        chunk['cross_encoder_score'] = sigmoid_score
        
    ranked_chunks = sorted(chunks, key=lambda x: x['cross_encoder_score'], reverse=True)
    return ranked_chunks[:top_k]
