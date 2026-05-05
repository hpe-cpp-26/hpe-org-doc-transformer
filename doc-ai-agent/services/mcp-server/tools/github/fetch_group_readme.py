from fastmcp import FastMCP
import logging 
from agent.schema import FetchGroupReadmeRequest, FetchGroupReadmeResponse

from services.github_service import GitHubReadmeService

logger = logging.getLogger(__name__)


def register_fetch_group_readme_tool(mcp: FastMCP):

    @mcp.tool
    async def fetch_group_readme(request: FetchGroupReadmeRequest) -> FetchGroupReadmeResponse:
        """
        Fetches the README content for a given GitHub group name.
        Args:
            request (FetchGroupReadmeRequest): The request object containing the GitHub group name.
        Returns:
            FetchGroupReadmeResponse: The response object containing the README content.
        """
        group_name = request.group_name
        logger.info("Fetching README for group: %s", group_name)

        service = GitHubReadmeService()
        readme_content = await service.get_group_readme_content(group_name)
        logger.info("Fetched README for group: %s", group_name)
        
        return FetchGroupReadmeResponse(
            group_name=group_name,
            readme_content=readme_content
        )

    