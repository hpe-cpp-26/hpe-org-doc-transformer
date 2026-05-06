from pydantic import BaseModel, Field

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


class SearchGroupChunksRequest(BaseModel):
    """
    Schema for the input to the search_group_chunks tool.
    """
    group_id: str = Field(..., description="The ID of the GitHub group to search chunks for.")
    embedding: list[float] = Field(..., description="The embedding vector to compare against the group chunks.")
    limit: int = Field(3, description="The maximum number of chunks to return.")
    


class SearchGroupChunksResponse(BaseModel):
    """
    Schema for the output from the search_group_chunks tool.
    """
    group_id: str = Field(..., description="The ID of the GitHub group.")
    chunks: list[dict] = Field(..., description="A list of matching chunks with their metadata and similarity scores.")


