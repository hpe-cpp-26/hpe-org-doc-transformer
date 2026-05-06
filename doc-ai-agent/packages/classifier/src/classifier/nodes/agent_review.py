import json
import logging
import re
from typing import Any
from agent.agent import build_agent
from agent.prompts.agent_review_prompt import _SYSTEM_PROMPT
from doc_types.state import ClassifierState
from classifier.utils.agent_review_utils import _build_user_message, _normalize_message_content, _parse_decision, _validate_decision

logger = logging.getLogger(__name__)

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