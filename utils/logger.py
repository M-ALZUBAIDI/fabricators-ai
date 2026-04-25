"""Logging configuration."""
import logging
import logging.config
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(environment: str = "development"):
    """Setup logging configuration."""

    log_level = "DEBUG" if environment == "development" else "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": LOG_DIR / "app.log",
            },
        },
        "loggers": {
            "": {  # root logger
                "level": log_level,
                "handlers": ["console", "file"],
            },
        },
    }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete - Environment: {environment}")
    return logger
