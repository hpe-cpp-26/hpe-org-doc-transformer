import logging
from config import get_settings, configure_logging
import asyncio

from doc_types.documents import NormalisedDocument
from graph.workflow import run_workflow

async def main():
    settings = get_settings(service_name="orchestrator")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Orchestrator service starting")

    #Example document for testing
    doc = NormalisedDocument(
        doc_id="123",
        source="github",
        title="Example Document",
        content="This is an example document for testing.",
        metadata={"author": "John Doe", "created_at": "2024-01-01"},
    )

    final_state = await run_workflow(doc)
    logger.info("Orchestrator service finished")
    logger.info(f"Final state: {final_state}")

if __name__ == "__main__":
    asyncio.run(main())
