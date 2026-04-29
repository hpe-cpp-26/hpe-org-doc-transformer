from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .settings import Settings, get_settings

@dataclass(frozen=True)  
class LoggingContext:
    """
    This is an immutable context object that holds metadata for log records.
    """
    service_name: str
    environment: str


class JsonFormatter(logging.Formatter):
    """
    converts log records into a structured JSON format with additional context information.
    """
    def __init__(self, context: LoggingContext, *, pretty: bool = False) -> None:
        super().__init__()
        self._context = context
        self._pretty = pretty

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self._context.service_name,
            "environment": self._context.environment,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if self._pretty:
            return json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True)
        return json.dumps(payload, ensure_ascii=True)


def _normalize_log_level(level: str) -> int:
    """
    fix any common mistakes in log level configuration and
    return a valid logging level integer.
    """
    normalized = level.strip().upper()
    #logging.INFO is the fallback here
    return logging._nameToLevel.get(normalized, logging.INFO)


def configure_logging(settings: Settings | None = None) -> None:
    resolved_settings = settings or get_settings()
    context = LoggingContext(
        service_name=resolved_settings.service_name,
        environment=resolved_settings.environment,
    )

    handler = logging.StreamHandler()
    log_format = resolved_settings.log_format.lower()
    if log_format == "json":
        handler.setFormatter(JsonFormatter(context))
    elif log_format in {"json_pretty", "pretty"}:
        handler.setFormatter(JsonFormatter(context, pretty=True))
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]

    #any log level less than the configured level wil be ignored
    #default to INFO if the config is invalid
    root_logger.setLevel(_normalize_log_level(resolved_settings.log_level))
