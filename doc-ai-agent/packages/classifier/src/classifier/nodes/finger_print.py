from doc_types.state import ClassifierState
from agent.llm import get_llm
from agent.prompts.fingerprint_prompt import FINGERPRINT_PROMPT
import json
import re
import logging

logger = logging.getLogger(__name__)


def _strip_json_fences(text: str) -> str:
    """Strip markdown code fences"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def generate_fingerprint(state: ClassifierState) -> ClassifierState:
    """Generates a semantic fingerprint for the document."""
    llm = get_llm(thinking=False)

    try:
        prompt_value = FINGERPRINT_PROMPT.invoke({
            "content": state["content"],
            "source": state["source"],
            "title": state["title"],
            "metadata": state["metadata"],
        })

        llm_response = llm.invoke(prompt_value)
        response_text = getattr(llm_response, "content", str(llm_response))
        cleaned = _strip_json_fences(response_text)
        
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and isinstance(parsed.get("fingerprint"), str):
                state["fingerprint"] = parsed["fingerprint"]
            else:
                state["fingerprint"] = cleaned
        except json.JSONDecodeError as e:
            logger.error(
                f"Fingerprint JSON parse failed for doc '{state.get('title', 'unknown')}': {e}\n"
                f"Raw response: {response_text[:500]}"
            )
            state["fingerprint"] = cleaned
            state.setdefault("errors", []).append(f"JSON parse error: {str(e)}")

    except Exception as e:
        logger.error(f"Error generating fingerprint for doc '{state.get('title', 'unknown')}': {e}")
        state["fingerprint"] = None
        state.setdefault("errors", []).append(f"Error generating fingerprint: {str(e)}")

    return state