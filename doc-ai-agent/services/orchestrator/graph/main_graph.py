from pathlib import Path
import sys

from langgraph.graph import StateGraph, END
from doc_types.state import ClassifierState

SERVICES_DIR = Path(__file__).resolve().parents[2]
if str(SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICES_DIR))

from classifier.nodes.validate_input import validate_input
from classifier.nodes.duplicate_check import duplicate_check


def build_graph():
    classifier = StateGraph(ClassifierState)

    classifier.add_node("validate_input" , validate_input)
    classifier.add_node("check_duplicate", duplicate_check)


    classifier.set_entry_point("validate_input")

    classifier.add_conditional_edges(
        "validate_input",
        lambda s: END if s["errors"] or not s["is_valid"] else "check_duplicate"
    )
    classifier.add_edge("check_duplicate", END)
    return classifier.compile()

