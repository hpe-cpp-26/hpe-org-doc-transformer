import json
import re
from typing import Any


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
