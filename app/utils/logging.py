"""
Logging configuration utilities.
"""

import logging

from app.core.config import get_settings

# Get settings
settings = get_settings()


def configure_logging() -> logging.Logger:
    """Configure application logging for container environments."""
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Console handler for stdout/stderr
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(console_handler)

    return logger
