import json
import logging
from datetime import date

from doc_types.state import ClassifierState
from agent.llm import get_llm
from agent.prompts.readme_prompt import UPDATE_GROUP_README_PROMPT
from classifier.ingestion.ingest import ingest_document
from classifier.utils.github_client import GitHubClient
from classifier.ingestion.detection import detect_doc_info
from classifier.ingestion.chunking import chunk_document
from classifier.ingestion.embedding import embed_chunks
from classifier.ingestion.segments import build_segment_embeddings
from db import get_connection
from config.settings import get_settings

logger = logging.getLogger(__name__)


def _resolve_group_name(state: ClassifierState) -> str | None:
    """
    Resolve the kebab-case GitHub folder name for the assigned group.

    The group router / agent_review stores a UUID in assigned_group_id /
    existing_group_id. The similar_group_candidates list carries both
    the UUID (id) and the slug (name), so we look there first.
    If we cannot find a slug we fall back to using the ID string directly
    (works fine when the pipeline is run without a real DB — e.g. in test mode).
    """
    target_id = state.get("assigned_group_id") or state.get("existing_group_id")
    if not target_id:
        return None

    # Try to resolve UUID → slug from candidate list
    candidates: list[dict] = state.get("similar_group_candidates") or []
    for c in candidates:
        cid = c.get("id") or c.get("group_id")
        if cid == target_id:
            name = c.get("name") or c.get("group_name")
            if name:
                return str(name)

    # Fall back: use the ID as-is (may be a slug already, e.g. in test mode)
    return str(target_id)


async def auto_assign(state: ClassifierState) -> ClassifierState:
    """
    LangGraph node — ASSIGN path.

    1. Resolve the target group's kebab-case name.
    2. Fetch the group's current README from GitHub.
    3. Call the LLM to produce an updated README that blends in the new doc.
    4. Commit the updated README back to GitHub.
    5. Update state markers.
    """
    errors: list[str] = list(state.get("errors") or [])
    decision_path: list[str] = list(state.get("decision_path") or [])

    group_name = _resolve_group_name(state)
    if not group_name:
        err = "assign_node: cannot determine group_name — assigned_group_id is missing"
        logger.error(err)
        errors.append(err)
        state["github_write_status"] = "error"
        state["readme_update_status"] = "error"
        state["errors"] = errors
        decision_path.append("assign_node")
        state["decision_path"] = decision_path
        return state

    logger.info("assign_node: updating README for group '%s'", group_name)

    github = GitHubClient()
    try:
        # --- 1. Fetch current README ---
        try:
            current_readme = await github.get_readme(group_name)
        except Exception as fetch_exc:
            # If the README doesn't exist yet, start from an empty document
            logger.warning(
                "assign_node: could not fetch README for '%s': %s — starting fresh",
                group_name,
                fetch_exc,
            )
            current_readme = f"# {group_name}\n\n_No README found. This file will be created._\n"

        # --- 2. Generate updated README via LLM ---
        llm = get_llm(thinking=False)
        prompt_value = UPDATE_GROUP_README_PROMPT.invoke(
            {
                "current_readme": current_readme,
                "title": state.get("title", "N/A"),
                "source": state.get("source", "N/A"),
                "fingerprint": state.get("fingerprint", "N/A"),
                "metadata": json.dumps(state.get("metadata") or {}, indent=2),
                "content": (state.get("content") or ""),
                "today": date.today().isoformat(),
            }
        )
        llm_response = llm.invoke(prompt_value)
        updated_readme = getattr(llm_response, "content", str(llm_response)).strip()

        logger.debug(
            "assign_node: generated updated README for '%s' (%d chars)",
            group_name,
            len(updated_readme),
        )

        commit_message = (
            f"chore: assign doc '{state.get('doc_id')}' to group '{group_name}'"
        )
        await github.update_readme(group_name, updated_readme, commit_message)

        base_path = get_settings().github_base_path
        source = state.get("source") or "unknown-source"
        doc_id = state.get("doc_id") or "unknown-doc"
        doc_filename = doc_id if doc_id.lower().endswith(".md") else f"{doc_id}.md"
        doc_path = state.get("existing_path") or (
            f"{base_path}/{group_name}/{source}/{doc_filename}"
        )
        await github.create_or_update_file(
            doc_path,
            state.get("content") or "",
            f"chore: update doc '{doc_id}' in group '{group_name}'",
        )

        # --- 4. Update state markers ---
        state["github_write_status"] = "updated"
        state["readme_update_status"] = "updated"
        # keep assigned_group_id as the DB group id
        decision_path.append("assign_node")
        state["decision_path"] = decision_path

        logger.info("assign_node: README for group '%s' updated successfully", group_name)

        # --- 5. Assign the document to the group and update prototypes ---
        group_id = state.get("assigned_group_id") or state.get("existing_group_id")
        if group_id:
            try:
                content = state.get("content") or ""
                doc_info = detect_doc_info(content, title=state.get("title"))
                doc_id = state.get("doc_id") or "unknown-doc"
                base_path = get_settings().github_base_path
                source = state.get("source") or "unknown-source"
                doc_filename = (
                    doc_id if doc_id.lower().endswith(".md") else f"{doc_id}.md"
                )
                doc_path = state.get("existing_path") or (
                    f"{base_path}/{group_name}/{source}/{doc_filename}"
                )

                chunks = chunk_document(content, doc_info)
                embed_chunks(chunks)
                segments = build_segment_embeddings(chunks)

                with get_connection() as conn:
                    with conn.transaction():
                        ingest_document(
                            doc_id=doc_id,
                            doc_path=doc_path,
                            group_id=group_id,
                            content=content,
                            doc_info=doc_info,
                            chunks=chunks,
                            segments=segments,
                            conn=conn,
                        )
                state["db_update_status"] = "updated"
                logger.info(
                    "assign_node: DB updated for group '%s' (doc_id=%s)",
                    group_name, doc_id,
                )
            except Exception as db_exc:
                logger.error(
                    "assign_node: DB write failed for group '%s': %s",
                    group_name, db_exc,
                )
                errors.append(f"assign_node DB write: {type(db_exc).__name__}: {db_exc}")
                state["db_update_status"] = "error"
        else:
            logger.warning(
                "assign_node: missing group_id — skipping DB write for group '%s'",
                group_name,
            )
            state["db_update_status"] = "skipped"

    except Exception as exc:
        error_msg = f"assign_node: {type(exc).__name__}: {exc}"
        logger.exception("assign_node: failed to update README for group '%s'", group_name)
        errors.append(error_msg)
        state["github_write_status"] = "error"
        state["readme_update_status"] = "error"
        decision_path.append("assign_node")
        state["decision_path"] = decision_path

    finally:
        await github.aclose()

    state["errors"] = errors if errors else None
    return state
