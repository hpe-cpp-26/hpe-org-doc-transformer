import logging
import asyncio
from typing import Any

from config import get_settings, configure_logging
from doc_types.state import ClassifierState

# from test_data import (
#     doc_auto_assign_payment,
#     doc_review_agent_self_healing,
#     doc_create_new_group,
#     doc_review_agent_ambiguous,
# )

from graph.workflow import run_workflow
from doc_types.documents import NormalisedDocument
from formatting import SEPARATOR, print_doc_header, print_result
from rabbitmq.consumer import RabbitMQConsumer


async def process_normalised_document(doc_dict: dict[str, Any]):
    try:
        doc= NormalisedDocument(**doc_dict)
        print_doc_header(doc)
        final_state = await run_workflow(doc)
        print_result(final_state)
    except Exception as e:
        logging.error(f"Error creating NormalisedDocument: {e}")
        raise
    

# TEST_DOCS = [
#     doc_auto_assign_payment,
#     doc_review_agent_self_healing,
#     doc_create_new_group,
#     doc_review_agent_ambiguous,
# ]

async def main():
    settings = get_settings(service_name="orchestrator")
    configure_logging(settings)
    logger = logging.getLogger(__name__)
    
    print(f"\n{SEPARATOR}")
    print("    ORCHESTRATOR — CLASSIFIER PIPELINE TEST")
    print(f"    Listening on: {settings.rabbitmq_queue}")
    print(f"    RabbitMQ: {settings.rabbitmq_url}")
    print(SEPARATOR)

    consumer = RabbitMQConsumer()
    try:
        await consumer.connect()
        await consumer.declare_queue()

        logger.info(f"Connected to RabbitMQ and declared queue. Starting to consume messages...")
        await consumer.consume_messages(callback=process_normalised_document)
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