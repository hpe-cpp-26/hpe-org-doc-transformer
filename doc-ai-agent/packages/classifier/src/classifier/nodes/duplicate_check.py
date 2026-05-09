
from doc_types.state import ClassifierState
from db.vector_queries import get_document_assignment
from doc_types.documents import DocumentAssignment
from db.connection import DatabaseConnectionError
import logging


logger = logging.getLogger(__name__)

def duplicate_check(state: ClassifierState) -> ClassifierState:

    """check if document already exists in the central repo
    if doc_id already exists -> marks as duplicate and adds existing group 
    and doc info to state"""

    doc_id = state.get("doc_id")
    try:
        res: DocumentAssignment = get_document_assignment(doc_id)

        if res is not None and res.group_id is not None:
            state["is_duplicate"] = True
            state["existing_group_id"] = res.group_id
            state["existing_path"] = res.path
            state["embedding"] = res.embedding
            state["classification_route"] = "AUTO_ASSIGN"
            state["create_new_group"] = False
        else:
            state["is_duplicate"] = False

    except DatabaseConnectionError as exc:
        logger.error(
            "Database connection error during duplicate check",
            extra={"doc_id": doc_id},
            exc_info=exc,
        )
        state["is_duplicate"] = False
        state.setdefault("errors", []).append(
            "Database connection error during duplicate check"
        )

    state["decision_path"].append("check_duplicate")
    return state

