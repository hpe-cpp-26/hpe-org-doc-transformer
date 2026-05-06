

from fastmcp import FastMCP
from agent.schema import SearchGroupChunksRequest, SearchGroupChunksResponse
from services.search_service import SearchService


def register_search_group_chunks_tool(mcp: FastMCP):

    @mcp.tool
    def search_group_chunks(request: SearchGroupChunksRequest) -> SearchGroupChunksResponse:
        """
        This tool will be used to find the most relevant chunks of information for a given query embedding.
        Input:
    - request.group_id: The ID of the group to search within.
    - request.embedding: The embedding vector representing the query.
    - request.limit: The maximum number of chunks to return.
        Output:
    - A list of the most relevant chunks, each with its metadata and similarity score.  
        """
        search_service = SearchService()
        
        group_chunks :list[dict]= search_service.fetch_group_chunks(request.group_id, request.embedding, request.limit)

        return SearchGroupChunksResponse(
            group_id=request.group_id,
            chunks=group_chunks
        )
    