import json
import logging
import re
from typing import Any
from agent.agent import build_agent
from agent.prompts.agent_review_prompt import _SYSTEM_PROMPT
from doc_types.state import ClassifierState

logger = logging.getLogger(__name__)

VALID_DECISIONS = {"ASSIGN", "CREATE_NEW"}


def _build_user_message(state: dict) -> str:

    candidates = state.get("similar_group_candidates") or []
    if not candidates:
        candidates_text = "No candidate groups found."
        instruction = (
            "No existing groups are similar. Decide whether to CREATE_NEW."
        )
    else:
        lines = []
        for c in candidates:
            group_id = c.get("id") or c.get("group_id") or "unknown"
            similarity = c.get("similarity") or c.get("score") or 0.0
            lines.append(
                f"- {c.get('name', 'unknown')} "
                f"(id={group_id}, similarity={float(similarity):.3f})"
            )
        candidates_text = "\n".join(lines)

        instruction = (
            "For EACH candidate group, you MUST call the tool "
            "`fetch_group_readme` using its group_name before deciding.\n"
            "Do NOT make a decision without reading all README contents."
        )

    return f"""
New document to classify:

Title      : {state.get('title', 'N/A')}
Source     : {state.get('source', 'N/A')}
Fingerprint: {state.get('fingerprint', 'N/A')}
Metadata   : {json.dumps(state.get('metadata', {}), indent=2)}

Candidate groups:
{candidates_text}

Top similarity score: {state.get('top_similarity_score', 0.0):.3f}

Instructions:
{instruction}

Return ONLY valid JSON in this format:

{{
    "decision": "ASSIGN" | "CREATE_NEW",
    "assigned_group_id": string | null,
    "confidence": float (0 to 1),
    "reasoning": string
}}
""".strip()


def _normalize_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or item))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def _parse_decision(raw: str) -> dict[str, Any]:
    clean = raw.strip()

    #extract first JSON object
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response")

    return json.loads(match.group())

def _validate_decision(decision: dict) -> dict:
    decision_type = decision.get("decision")

    if decision_type not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision: {decision_type}")

    confidence = float(decision.get("confidence", 0.0))
    confidence = max(0.0, min(1.0, confidence))  # clamp

    assigned_group_id = decision.get("assigned_group_id")
    if decision_type == "CREATE_NEW":
        assigned_group_id = None

    return {
        "decision": decision_type,
        "assigned_group_id": assigned_group_id,
        "confidence": confidence,
        "reasoning": decision.get("reasoning", ""),
    }


async def agent_review(state: ClassifierState) -> ClassifierState:
    errors = list(state.get("errors") or [])

    try:
        async with build_agent(thinking=True) as agent:
            result = await agent.ainvoke({
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_message(state)},
                ]
            })

        last_message = result["messages"][-1].content
        normalized_message = _normalize_message_content(last_message)

        decision_raw = _parse_decision(normalized_message)
        decision = _validate_decision(decision_raw)

        logger.info(
            "Agent decision: %s | group: %s | confidence: %.2f",
            decision["decision"],
            decision["assigned_group_id"],
            decision["confidence"],
        )

        state["agent_decision"] = decision
        state["create_new_group"] = decision["decision"] == "CREATE_NEW"
        if decision["decision"] == "ASSIGN":
            state["assigned_group_id"] = decision["assigned_group_id"]
            state["existing_group_id"] = decision["assigned_group_id"]
        else:
            state["assigned_group_id"] = None

        decision_path = state.get("decision_path")
        if isinstance(decision_path, list):
            decision_path.append("agent_review")
        else:
            state["decision_path"] = ["agent_review"]
        return state

    except json.JSONDecodeError as e:
        errors.append(f"agent_review: JSON parse failed: {e}")
        logger.error("agent_review: JSON parse failed: %s", e)

    except Exception as e:
        errors.append(f"agent_review: {type(e).__name__}: {e}")
        logger.exception("agent_review: unexpected error")

    # Conservative fallback
    state["agent_decision"] = {
        "decision": "CREATE_NEW",
        "assigned_group_id": None,
        "confidence": 0.0,
        "reasoning": "Defaulted to CREATE_NEW due to error in agent review process.",
    }
    state["create_new_group"] = True
    state["assigned_group_id"] = None

    decision_path = state.get("decision_path")
    if isinstance(decision_path, list):
        decision_path.append("agent_review")
    else:
        state["decision_path"] = ["agent_review"]

    errors.append("agent_review: fallback to CREATE_NEW")
    state["errors"] = errors
    return state