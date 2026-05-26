import logging
import base64
import httpx
from typing import Optional

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

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _readme_url(self, group_name: str) -> str:
        file_path = f"{self._base_path}/{group_name}/README.md"
        return f"{self._api_url}/repos/{self._org}/{self._repo}/contents/{file_path}"

    async def _get_file_sha(self, group_name: str) -> Optional[str]:
        """Return the blob SHA of an existing README, or None if it doesn't exist."""
        try:
            response = await self._client.get(
                self._readme_url(group_name), headers=self._build_headers()
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json().get("sha")
        except httpx.HTTPStatusError:
            return None

    async def create_group_with_readme(
        self,
        group_name: str,
        readme_content: str,
        commit_message: str = "chore: create new document group via doc-ai-agent",
    ) -> dict:
        """
        Create a new group folder by writing README.md at:
            {base_path}/{group_name}/README.md
        Raises if the file already exists (GitHub returns 422).
        """
        encoded = base64.b64encode(readme_content.encode("utf-8")).decode("utf-8")
        payload = {"message": commit_message, "content": encoded}

        response = await self._client.put(
            self._readme_url(group_name),
            headers=self._build_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(
            "Created README for group=%s | commit=%s",
            group_name,
            data.get("commit", {}).get("sha", ""),
        )
        # Invalidate cache entry if present
        self._cache.pop(group_name, None)
        return data

    async def update_group_readme(
        self,
        group_name: str,
        new_content: str,
        commit_message: str = "chore: update group README via doc-ai-agent",
    ) -> dict:
        """
        Overwrite an existing group README.md. Fetches the current SHA first
        (required by the GitHub Contents API for updates).
        """
        sha = await self._get_file_sha(group_name)
        if sha is None:
            logger.warning(
                "README for group=%s not found; creating instead of updating.",
                group_name,
            )
            return await self.create_group_with_readme(group_name, new_content, commit_message)

        encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        payload = {"message": commit_message, "content": encoded, "sha": sha}

        response = await self._client.put(
            self._readme_url(group_name),
            headers=self._build_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(
            "Updated README for group=%s | commit=%s",
            group_name,
            data.get("commit", {}).get("sha", ""),
        )
        self._cache.pop(group_name, None)
        return data