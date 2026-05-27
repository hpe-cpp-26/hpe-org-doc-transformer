import json
import logging
import re
import uuid
from datetime import date

from doc_types.state import ClassifierState
from agent.llm import get_llm
from agent.prompts.readme_prompt import NEW_GROUP_README_PROMPT
from classifier.ingestion.ingest import detect_doc_info, ingest_document
from classifier.prototypes import assign_group
from classifier.utils.github_client import GitHubClient
from db import insert_new_group

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    """Convert a plain-text string to a kebab-case slug suitable for a GitHub folder name."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text[:60].strip("-")


def _resolve_group_name(state: ClassifierState) -> str:
    """
    Determine the new group's kebab-case folder name.

    Priority:
    1. agent_decision["new_group_name"]  (set by agent_review when it picks CREATE_NEW)
    2. metadata["project"]
    3. slugified title
    """
    agent_decision = state.get("agent_decision") or {}
    candidate = agent_decision.get("new_group_name")
    if candidate and isinstance(candidate, str) and candidate.strip():
        return _slugify(candidate)

    project = (state.get("metadata") or {}).get("project")
    if project and isinstance(project, str) and project.strip():
        return _slugify(project)

    title = state.get("title") or state.get("doc_id") or "new-group"
    return _slugify(title)


def _resolve_group_description(state: ClassifierState) -> str:
    """Pull description from agent_decision or fall back to a generic string."""
    agent_decision = state.get("agent_decision") or {}
    desc = agent_decision.get("new_group_description")
    if desc and isinstance(desc, str) and desc.strip():
        return desc.strip()
    return f"Document group for {state.get('title', 'unknown project')}."


async def create_new_group(state: ClassifierState) -> ClassifierState:
    """
    LangGraph node — CREATE path.

    1. Resolve the group name (kebab-case slug).
    2. Call the LLM to generate a Markdown README.
    3. Commit README.md to GitHub under {base_path}/{group_name}/.
    4. Update state markers.
    """
    errors: list[str] = list(state.get("errors") or [])
    decision_path: list[str] = list(state.get("decision_path") or [])

    group_name = _resolve_group_name(state)
    group_description = _resolve_group_description(state)

    logger.info("create_node: creating new group '%s'", group_name)

    try:
      
        llm = get_llm(thinking=False)
        prompt_value = NEW_GROUP_README_PROMPT.invoke(
            {
                "group_name": group_name,
                "group_description": group_description,
                "title": state.get("title", "N/A"),
                "source": state.get("source", "N/A"),
                "fingerprint": state.get("fingerprint", "N/A"),
                "metadata": json.dumps(state.get("metadata") or {}, indent=2),
                "content": (state.get("content") or "")[:3000],
            }
        )
        llm_response = llm.invoke(prompt_value)
        readme_content = getattr(llm_response, "content", str(llm_response)).strip()

        logger.debug(
            "create_node: generated README for '%s' (%d chars)", group_name, len(readme_content)
        )

        
        github = GitHubClient()
        try:
            commit_message = (
                f"chore: create group '{group_name}' for doc '{state.get('doc_id')}'"
            )
            await github.create_readme(group_name, readme_content, commit_message)
        finally:
            await github.aclose()

       
        state["assigned_group_id"] = None
        state["github_write_status"] = "created"
        state["readme_update_status"] = "created"
        decision_path.append("create_node")
        state["decision_path"] = decision_path

        logger.info("create_node: group '%s' created successfully on GitHub", group_name)

       
        try:
            #new group created
            group_uuid = str(uuid.uuid4())
            insert_new_group(group_uuid, group_name, group_summary=readme_content)

            content = state.get("content") or ""
            doc_info = detect_doc_info(content, title=state.get("title"))
            
            #[TODO: Dharshan][mid]- set correct doc path
            doc_path =f"{group_name}/{state.get("source")}/{state.get('doc_id')}"
            ingest_document(
                doc_id=state["doc_id"],
                doc_path=doc_path,
                group_id=group_uuid,
                content=content,
                doc_info=doc_info,
            )

            # assign_group(state["doc_id"], group_uuid)
            state["assigned_group_id"] = group_uuid
            state["db_update_status"] = "created"
            logger.info(
                "create_node: DB row created for group '%s' (uuid=%s)",
                group_name, group_uuid,
            )
        except Exception as db_exc:
            logger.error(
                "create_node: DB write failed for group '%s': %s",
                group_name, db_exc,
            )
            errors.append(f"create_node DB write: {type(db_exc).__name__}: {db_exc}")
            state["db_update_status"] = "error"

    except Exception as exc:
        error_msg = f"create_node: {type(exc).__name__}: {exc}"
        logger.exception("create_node: failed to create group '%s'", group_name)
        errors.append(error_msg)
        state["github_write_status"] = "error"
        state["readme_update_status"] = "error"
        decision_path.append("create_node")
        state["decision_path"] = decision_path

    state["errors"] = errors if errors else None
    return state
