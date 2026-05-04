
from typing import Optional

from doc_types.state import ClassifierState


REQUIRED_FIELDS = ["doc_id", "source", "content", "metadata"]

def validate_input(state:ClassifierState) -> ClassifierState:
    
    """Validate and check for required fields in the input state."""
    errors =[]

    #check for required fields and empty content
    error = check_required_fields(state) or check_empty_content(state)
    if error:
        errors.append(error)
    state["errors"] = errors
    state["decision_path"].append("validate_input")
    return state

def check_required_fields(state:ClassifierState) -> Optional[str]:
    missing = [f for f in REQUIRED_FIELDS if f not in state.get(f)]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    return None

def check_empty_content(state:ClassifierState) -> Optional[str]:
    if not state.get("content", "").strip():
        return "Content field is empty"
    return None
