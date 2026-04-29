import logging

from config import configure_logging, get_settings


def main() -> None:
    settings = get_settings(service_name="classifier")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Classifier Service starting")


if __name__ == "__main__":
    main()
