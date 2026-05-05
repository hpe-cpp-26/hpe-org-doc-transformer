from pathlib import Path
import sys

from langgraph.graph import StateGraph, END
from doc_types.state import ClassifierState

from classifier.nodes.validate_input import validate_input
from classifier.nodes.duplicate_check import duplicate_check
from classifier.nodes.finger_print import generate_fingerprint
from classifier.nodes.group_router import decide_route
from classifier.nodes.agent_review import agent_review


def next_route(state: ClassifierState)-> str:
    if state["classification_route"]== "AUTO_ASSIGN":
        return END
    elif state["classification_route"]== "REVIEW_BY_AGENT":
        return "agent_review"
    else:
        return END

def build_graph():
    classifier = StateGraph(ClassifierState)
    
    #register nodes
    classifier.add_node("validate_input" , validate_input)
    classifier.add_node("check_duplicate", duplicate_check)
    classifier.add_node("generate_fingerprint", generate_fingerprint)
    classifier.add_node("decide_route", decide_route)
    classifier.add_node("agent_review", agent_review) 
    classifier.set_entry_point("validate_input")

    classifier.add_conditional_edges(
        "validate_input",
        lambda s: END if s["errors"] or not s["is_valid"] else "check_duplicate"
    )
    classifier.add_conditional_edges(
        "check_duplicate",
        lambda s: END if s["is_duplicate"] else "generate_fingerprint"
    )
    classifier.add_edge("generate_fingerprint", "decide_route")
    classifier.add_edge("decide_route", next_route)
    classifier.add_edge("agent_review", END)
    
    return classifier.compile()


