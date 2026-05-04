from doc_types.documents import NormalisedDocument
from doc_types.state import ClassifierState
from langgraph import graph
from graph.main_graph import build_graph
import logging

logger = logging.getLogger(__name__)

def build_initial_state(doc: NormalisedDocument)-> ClassifierState:
    """Builds the initial state for the document classification workflow."""

    return ClassifierState(
        #Normalised document data from the input
        doc_id=doc.doc_id,
        content=doc.content,
        source=doc.source,
        metadata=doc.metadata,
        title = doc.title,

        #rest of the state fields initialized to default values
        is_valid = True,

        #duplication checks
        is_duplicate=False,
        existing_group_id= None,
        existing_doc_id=None,

        #Embedding
        embedding=None,

        #Group centroid search
        similar_group_candidates=[],
        top_similarity_score=0.0,

        #classification result
        classification_result=None,

        #Agent context and decision making
        agent_context=None,
        group_readmes=None,
        sources_content_from_mcp=None,
        agent_decision=None,

        #Final Decision
        assinged_group_id =None,
        create_new_group=None,
        github_write_status=False,
        db_update_status=None,
        readme_update_status=None,

        #Audit and error handling
        decision_path=[],
        errors=None,
    )


def run_workflow(doc: NormalisedDocument)-> ClassifierState:
    """Runs the document classification workflow and returns the final state."""
    initial_state = build_initial_state(doc)
    graph=build_graph()
    logger.info("Running document classification workflow.")

    final_state = graph.ainvoke(initial_state)
    return final_state

