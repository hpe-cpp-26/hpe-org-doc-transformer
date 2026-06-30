# main.py

import logging
import asyncio
import sys
import os
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from config import get_settings, configure_logging
from doc_types.state import ClassifierState

from test_data import (
    doc_auto_assign_payment,
    doc_review_agent_self_healing,
    doc_create_new_group,
    doc_review_agent_ambiguous,
    doc_self_healing_github,
    doc_create_new_group_security,
)

from graph.workflow import run_workflow
from doc_types.documents import NormalisedDocument
from formatting import SEPARATOR, print_doc_header, print_result
from rabbitmq.consumer import RabbitMQConsumer


TEST_DOCS = [
    doc_auto_assign_payment,
    doc_review_agent_self_healing,
    doc_create_new_group,
    doc_review_agent_ambiguous,
    doc_self_healing_github,
    doc_create_new_group_security,
]


async def process_normalised_document(doc_dict: dict[str, Any]):
    try:
        doc = NormalisedDocument(**doc_dict)
        print_doc_header(doc)
        final_state = await run_workflow(doc)
        print_result(final_state)
    except Exception as e:
        logging.error(f"Error creating NormalisedDocument: {e}")
        raise


def _clear_test_docs_from_db(doc_ids: list[str]) -> None:
    """
    Remove test doc IDs from the `documents` table so they are not
    flagged as duplicates on the next test run.
    """
    from db.connection import get_connection

    logger = logging.getLogger(__name__)

    try:
        with get_connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM documents WHERE id = ANY(%s)",
                        [doc_ids],
                    )

        logger.info("Cleared %d test doc(s) from documents table.", len(doc_ids))

    except Exception as exc:
        logger.warning("Could not clear test docs from DB: %s", exc)


async def run_test_mode(fresh: bool = False) -> None:
    logger = logging.getLogger(__name__)

    if fresh:
        test_ids = [doc.doc_id for doc in TEST_DOCS]

        print(f"\n  [fresh] Clearing {len(test_ids)} test doc(s) from DB...")
        _clear_test_docs_from_db(test_ids)

    print(f"\n{SEPARATOR}")
    print("    ORCHESTRATOR — GITHUB INTEGRATION TEST MODE")
    print(f"    Running {len(TEST_DOCS)} test document(s) through the pipeline")
    print(SEPARATOR)

    for doc in TEST_DOCS:
        try:
            print_doc_header(doc)

            final_state = await run_workflow(doc)

            print_result(final_state)

            gws = final_state.get("github_write_status")
            rus = final_state.get("readme_update_status")
            group = final_state.get("assigned_group_id")

            print(f"  github_write_status  : {gws}")
            print(f"  readme_update_status : {rus}")
            print(f"  assigned_group_id    : {group}")

            print(SEPARATOR)

        except Exception as exc:
            logger.error(
                "Test run failed for doc '%s': %s",
                doc.doc_id,
                exc,
                exc_info=True,
            )

    print(f"\n{SEPARATOR}")
    print("    TEST MODE COMPLETE")
    print(f"{SEPARATOR}\n")


async def main():
    settings = get_settings(service_name="orchestrator")

    configure_logging(settings)

    logger = logging.getLogger(__name__)

    # TEST MODE
    if "--test" in sys.argv:
        fresh = "--fresh" in sys.argv

        await run_test_mode(fresh=fresh)

        return

    # NORMAL RABBITMQ MODE
    print(f"\n{SEPARATOR}")
    print("    ORCHESTRATOR — CLASSIFIER PIPELINE")
    print(f"    Listening on: {settings.rabbitmq_queue}")
    print(f"    RabbitMQ: {settings.rabbitmq_url}")
    print(SEPARATOR)

    consumer = RabbitMQConsumer()

    try:
        await consumer.connect()
        await consumer.declare_queue()

        logger.info(
            "Connected to RabbitMQ and declared queue. "
            "Starting to consume messages..."
        )

        await consumer.consume_messages(
            callback=process_normalised_document
        )

    except asyncio.CancelledError:
        logger.info("Shutting down consumer...")

    except Exception as e:
        logger.error(f"Error occurred while connecting to RabbitMQ: {e}")
        raise

    finally:
        print(f"{SEPARATOR}")
        print("   ALL DOCS PROCESSED")
        print(f"{SEPARATOR}\n")

        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())