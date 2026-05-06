import logging
from config.settings import get_settings
from db.vector_queries import search_similar_chunks_by_group

class SearchService:
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)


    def fetch_group_chunks(self, group_id: str, embedding: list[float], limit: int) -> list[dict]:
        
        self.logger.info(f"Fetching chunks for group_id: {group_id} with limit: {limit}")

        chunks = search_similar_chunks_by_group(group_id=group_id, embedding=embedding, limit=limit)

        return chunks
        

