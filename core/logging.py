"""Structlog configuration module.

Features:
 - JSON output in non-local environments.
 - Human-readable console output in local/dev.
 - DEBUG level in local/dev; INFO elsewhere (override with LOG_LEVEL env var).
 - ContextVars support for request correlation (request_id).
"""

import logging

import structlog

from core.settings import settings


def configure_logging() -> None:
    """Configure structlog and stdlib logging for the application."""
    desired_level = (
        settings.LOG_LEVEL
        or ("DEBUG" if settings.APP_ENV in ("local", "dev") else "INFO")
    ).upper()
    level = getattr(logging, desired_level, logging.INFO)

    logging.basicConfig(level=level, format="%(message)s")

    # Select renderer based on environment
    if settings.APP_ENV in ("local", "dev"):
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger():
    """Get a structlog logger instance."""
    return structlog.get_logger()
