import logging

from config import configure_logging, get_settings


def main() -> None:
    settings = get_settings(service_name="worker")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Worker Service starting")


if __name__ == "__main__":
    main()
