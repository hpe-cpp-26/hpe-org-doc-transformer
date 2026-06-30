import logging
from config.settings import get_settings
from db import search_similar_chunks_by_group, fetch_embedding_from_cache

class SearchService:
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)


    def fetch_group_chunks(self, group_id: str, doc_id: str, limit: int) -> list[dict]:
        
        self.logger.info(f"Fetching chunks for group_id: {group_id} with limit: {limit}")
        embedding = fetch_embedding_from_cache(doc_id)
        if embedding is None:
            self.logger.warning("No cached embedding found for doc_id: %s", doc_id)
            return []
        chunks = search_similar_chunks_by_group(group_id=group_id, embedding=embedding, limit=limit)

        return chunks

    # def fetch_global_chunks(self, doc_id: str, limit: int) -> list[dict]:
    #     self.logger.info(f"Fetching global chunks for doc_id: {doc_id} with limit: {limit}")
    #     embedding = fetch_embedding_from_cache(doc_id)
    #     if embedding is None:
    #         self.logger.warning("No cached embedding found for doc_id: %s", doc_id)
    #         return []
    #     chunks = search_similar_chunks_global(embedding=embedding, limit=limit)
    #     return chunks
        

