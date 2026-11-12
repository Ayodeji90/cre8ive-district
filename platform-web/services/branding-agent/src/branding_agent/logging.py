import logging
import sys

import structlog


def configure_logging(env: str = "development") -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if env == "development" else logging.INFO,
    )
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]
    processors.append(
        structlog.dev.ConsoleRenderer()
        if env == "development"
        else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if env == "development" else logging.INFO
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "branding_agent") -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
