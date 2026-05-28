"""
Lightweight GitHub REST client used by classifier nodes (create_node, assign_node).

This mirrors the GitHubService in services/mcp-server but lives in the classifier
package so the orchestrator nodes can instantiate it directly without going through
the MCP server transport layer.
"""

import base64
import logging
from typing import Optional

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()


class GitHubClient:
    """Async GitHub Contents-API client for reading and writing group READMEs."""

    def __init__(self) -> None:
        limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
        self._client = httpx.AsyncClient(timeout=30.0, limits=limits)
        self._api_url = _settings.github_api_url.rstrip("/")
        self._org = _settings.github_org
        self._repo = _settings.github_repo
        self._token = _settings.github_token
        self._base_path = _settings.github_base_path

    async def aclose(self) -> None:
        await self._client.aclose()

   
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _file_url(self, file_path: str) -> str:
        return f"{self._api_url}/repos/{self._org}/{self._repo}/contents/{file_path}"

    def _readme_path(self, group_name: str) -> str:
        return f"{self._base_path}/{group_name}/README.md"

    async def _get_file_sha(self, file_path: str) -> Optional[str]:
        """Return the blob SHA of an existing file, or None if it doesn't exist."""
        try:
            resp = await self._client.get(self._file_url(file_path), headers=self._headers())
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("sha")
        except httpx.HTTPStatusError:
            return None

    
    async def get_readme(self, group_name: str) -> str:
        """Fetch and decode the README.md for *group_name*. Raises on HTTP errors."""
        resp = await self._client.get(self._file_url(self._readme_path(group_name)), headers=self._headers())
        resp.raise_for_status()
        data = resp.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        logger.info("Fetched README for group=%s", group_name)
        return content

    async def create_or_update_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
    ) -> dict:
        encoded = base64.b64encode(content.encode()).decode()
        payload = {"message": commit_message, "content": encoded}

        sha = await self._get_file_sha(file_path)
        if sha is not None:
            payload["sha"] = sha

        resp = await self._client.put(
            self._file_url(file_path), headers=self._headers(), json=payload
        )
        resp.raise_for_status()
        return resp.json()

    async def create_readme(
        self,
        group_name: str,
        readme_content: str,
        commit_message: str = "chore: create new document group via doc-ai-agent",
    ) -> dict:
        """
        Create or update {base_path}/{group_name}/README.md.
        If file exists, fetches its SHA and updates it.
        If file doesn't exist, creates it.
        """
        data = await self.create_or_update_file(
            self._readme_path(group_name),
            readme_content,
            commit_message,
        )
        logger.info(
            "Created/Updated README for group=%s | commit=%s",
            group_name,
            data.get("commit", {}).get("sha", ""),
        )
        return data

    async def update_readme(
        self,
        group_name: str,
        new_content: str,
        commit_message: str = "chore: update group README via doc-ai-agent",
    ) -> dict:
        """
        Overwrite an existing README.md. Fetches the current SHA first.
        Falls back to create_readme if the file doesn't exist.
        """
        data = await self.create_or_update_file(
            self._readme_path(group_name),
            new_content,
            commit_message,
        )
        logger.info(
            "Updated README for group=%s | commit=%s",
            group_name,
            data.get("commit", {}).get("sha", ""),
        )
        return data
