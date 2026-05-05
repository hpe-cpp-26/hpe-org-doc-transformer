import logging
import asyncio

from config import get_settings, configure_logging
from test_data import doc_auto_assign_payment, doc_review_agent_self_healing, doc_create_new_group
from graph.workflow import run_workflow
from doc_types.documents import NormalisedDocument
from formatting import SEPARATOR, print_doc_header, print_result


async def _run_doc(doc: NormalisedDocument) -> dict:
    print_doc_header(doc)
    final_state = await run_workflow(doc)
    print_result(final_state)
    return final_state


TEST_DOCS = [
    doc_auto_assign_payment,
    doc_review_agent_self_healing,
    doc_create_new_group,
]

async def main():
    settings = get_settings(service_name="orchestrator")
    configure_logging(settings)
    logger = logging.getLogger(__name__)

    print(f"\n{SEPARATOR}")
    print("    ORCHESTRATOR — CLASSIFIER PIPELINE TEST")
    print(SEPARATOR)

    final_state=await _run_doc(TEST_DOCS[1])

    print(f"{SEPARATOR}")
    print("   ALL DOCS PROCESSED")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    asyncio.run(main())