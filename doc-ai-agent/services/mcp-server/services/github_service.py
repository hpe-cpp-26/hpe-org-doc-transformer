import logging
import base64
import httpx

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings(service_name="mcp-server")


class GitHubService:
    def __init__(self) -> None:

        limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
        self._client = httpx.AsyncClient(timeout=30.0, limits=limits)

        self._api_url = settings.github_api_url.rstrip("/")
        self._org = settings.github_org
        self._repo = settings.github_repo 
        self._token = settings.github_token
        self._base_path = settings.github_base_path 
        self._cache: dict[str, str] = {}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_group_readme_content(self, group_name: str) -> str:
        """
        group_name:"self-healing-system"
        """
        if not group_name:
            raise ValueError("group_name cannot be empty")
        
        if group_name in self._cache:
            return self._cache[group_name]

        file_path = f"{self._base_path}/{group_name}/README.md"

        url = (
            f"{self._api_url}/repos/"
            f"{self._org}/{self._repo}/contents/{file_path}"
        )

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            content = base64.b64decode(data["content"]).decode("utf-8")

            self._cache[group_name] = content

            logger.info("Fetched README for group: %s", group_name)

            return content

        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to fetch README for group=%s | status=%s | error=%s",
                group_name,
                e.response.status_code,
                e.response.text,
            )
            raise