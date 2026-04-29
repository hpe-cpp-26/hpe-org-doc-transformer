"""Small action helpers for post-classification routing.

These are lightweight stubs so the classifier can trigger the
appropriate side-effects (GitHub update, agent routing, human flagging).
Replace with real implementations as needed.
"""
from typing import Any, Iterable


def github_update_readme_and_index(document_id: str, group_id: str) -> None:
    """Stub: update README and index.json via GitHub APIs.

    Replace with an implementation that uses the repository's GitHub
    credentials and APIs (or a dedicated service) to update project
    metadata after an automatic assignment.
    """
    print(f"[github_update] document={document_id} assigned→group={group_id}")


def route_to_agent(document: Any, candidate_groups: Iterable[dict]) -> None:
    """Stub: hand off the document and candidate groups to the Agent service.

    The Agent can perform richer inspection (MCP tools, LLM + tool calls)
    and decide whether to merge, create, or flag the document.
    """
    print(f"[route_to_agent] document={getattr(document, 'id', 'unknown')} candidates={len(list(candidate_groups))}")


# def flag_for_human_review(document_id: str, reason: str | None = None) -> None:
#     """Stub: flag document for human review (ticketing, DB flag, etc.)."""
#     print(f"[flag_human_review] document={document_id} reason={reason}")

def create_new_group(document_id: str) -> None:
    """Stub: create a new group for the document."""
    print(f"[create_new_group] document={document_id} - new group created")
    