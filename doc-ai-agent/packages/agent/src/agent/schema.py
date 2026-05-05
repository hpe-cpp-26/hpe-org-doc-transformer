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


