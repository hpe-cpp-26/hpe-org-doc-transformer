from pathlib import Path
import sys

from langgraph.graph import StateGraph, END
from doc_types.state import ClassifierState

from classifier.nodes.validate_input import validate_input
from classifier.nodes.duplicate_check import duplicate_check
from classifier.nodes.finger_print import generate_fingerprint
from classifier.nodes.group_router import decide_route
from classifier.nodes.agent_review import agent_review
from classifier.nodes.create_node import create_new_group
from classifier.nodes.assign_node import auto_assign
def next_route(state: ClassifierState)-> str:
    if state["classification_route"]== "AUTO_ASSIGN":
        return "assign_node"
    elif state["classification_route"]== "REVIEW_BY_AGENT":
        return "agent_review"
    elif state["classification_route"]== "CREATE_NEW_GROUP":
        return "create_node"
    else:
        return END

def agent_review_route(state: ClassifierState)-> str:
    if state.get("classification_route") == "CREATE_NEW_GROUP":
        return "create_node"
    elif state.get("classification_route") == "AUTO_ASSIGN":
        return "assign_node"
    else:
        return END

def build_graph():
    classifier = StateGraph(ClassifierState)
    
    classifier.add_node("validate_input" , validate_input)
    classifier.add_node("check_duplicate", duplicate_check)
    classifier.add_node("generate_fingerprint", generate_fingerprint)
    classifier.add_node("decide_route", decide_route)
    classifier.add_node("agent_review", agent_review) 
    classifier.add_node("create_node", create_new_group)
    classifier.add_node("assign_node", auto_assign)
    classifier.set_entry_point("validate_input")

    classifier.add_conditional_edges(
        "validate_input",
        lambda s: END if s["errors"] or not s["is_valid"] else "check_duplicate"
    )
    classifier.add_conditional_edges(
        "check_duplicate",
        lambda s: "assign_node" if s["is_duplicate"] else "generate_fingerprint"
    )
    classifier.add_edge("generate_fingerprint", "decide_route")
    classifier.add_conditional_edges("decide_route", next_route)
    classifier.add_conditional_edges("agent_review", agent_review_route)
    classifier.add_edge("create_node", END)
    classifier.add_edge("assign_node", END)
    
    return classifier.compile()


