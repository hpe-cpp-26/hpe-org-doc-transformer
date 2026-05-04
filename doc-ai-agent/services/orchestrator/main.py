import logging
from config.settings import get_settings, configure_logging



def main():
    settings = get_settings(service_name="orchestrator")
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info("Orchestrator service starting")


if __name__ == "__main__":
    main()
