from fastmcp import FastMCP
import logging 
from agent.schema import FetchGroupReadmeRequest, FetchGroupReadmeResponse

from services.github_service import GitHubService

logger = logging.getLogger(__name__)


def register_fetch_group_readme_tool(mcp: FastMCP):

    @mcp.tool
    async def fetch_group_readme(request: FetchGroupReadmeRequest) -> FetchGroupReadmeResponse:
        """
        Fetch README content for a group name under the configured org/repo.
        Input:
            request.group_name: subpath under the base path (for example "self-healing-system").
        Resolves to:
            {GITHUB_ORG}/{GITHUB_REPO}/contents/{GITHUB_BASE_PATH}/{group_name}/README.md
        Returns:
            README content as plain text in FetchGroupReadmeResponse.
        """
        group_name = request.group_name
        logger.info("Fetching README for group: %s", group_name)

        github_service = GitHubService()
        readme_content = await github_service.get_group_readme_content(group_name)
        logger.info("Fetched README for group: %s", group_name)
        
        return FetchGroupReadmeResponse(
            group_name=group_name,
            readme_content=readme_content
        )

    