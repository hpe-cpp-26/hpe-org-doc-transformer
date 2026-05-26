import json
import logging
from datetime import date

from doc_types.state import ClassifierState
from agent.llm import get_llm
from agent.prompts.readme_prompt import UPDATE_GROUP_README_PROMPT
from classifier.utils.github_client import GitHubClient
from db.connection import get_connection
from db.vector_queries import insert_document, update_centroid

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
                "content": (state.get("content") or "")[:3000],
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

        # --- 3. Commit to GitHub ---
        commit_message = (
            f"chore: assign doc '{state.get('doc_id')}' to group '{group_name}'"
        )
        await github.update_readme(group_name, updated_readme, commit_message)

        # --- 4. Update state markers ---
        state["github_write_status"] = "updated"
        state["readme_update_status"] = "updated"
        state["assigned_group_id"] = group_name   # surface the resolved group name
        decision_path.append("assign_node")
        state["decision_path"] = decision_path

        logger.info("assign_node: README for group '%s' updated successfully", group_name)

        # --- 5. Persist the document and update group centroid in the DB ---
        group_id = state.get("assigned_group_id") or state.get("existing_group_id")
        embedding: list[float] | None = state.get("embedding")
        if group_id and embedding:
            try:
                insert_document(
                    document_id=state["doc_id"],
                    path=state.get("source"),
                    group_id=group_id,
                    content=state.get("content"),
                    embedding=embedding,
                )

                # Incrementally update the centroid: weighted average of old centroid + new doc
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT centroid, doc_count FROM groups WHERE id = %s",
                            [group_id],
                        )
                        row = cur.fetchone()

                if row and row.get("centroid") is not None:
                    import ast
                    raw_centroid = row["centroid"]
                    # pgvector returns centroid as a string '[0.1,...]' in psycopg3
                    if isinstance(raw_centroid, str):
                        raw_centroid = ast.literal_eval(raw_centroid)
                    old_centroid = [float(v) for v in raw_centroid]
                    old_count = row.get("doc_count") or 1
                    new_count = old_count + 1
                    # Weighted average: (old_centroid * old_count + new_embedding) / new_count
                    new_centroid = [
                        (old_centroid[i] * old_count + embedding[i]) / new_count
                        for i in range(len(embedding))
                    ]
                    update_centroid(group_id, new_centroid, doc_count=new_count)
                else:
                    # No existing centroid — set this doc's embedding as the centroid
                    update_centroid(group_id, embedding, doc_count=1)

                state["db_update_status"] = "updated"
                logger.info(
                    "assign_node: DB updated for group '%s' (doc_id=%s)",
                    group_name, state["doc_id"],
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
                "assign_node: missing group_id or embedding — skipping DB write for group '%s'",
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
