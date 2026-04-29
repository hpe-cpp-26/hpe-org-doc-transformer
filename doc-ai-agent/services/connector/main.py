import logging

from config import configure_logging, get_settings


def main() -> None:
    settings = get_settings(service_name="connector")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Connector Service starting")


if __name__ == "__main__":
    main()
