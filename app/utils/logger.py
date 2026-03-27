import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure and return the application-wide logger.

    File logging is disabled when LOG_TO_FILE=0 or when running inside a
    container that sets RAILWAY_ENVIRONMENT or DOCKER_ENV, so that logs go
    only to stderr (captured by the platform's log aggregator).
    """
    logger = logging.getLogger("stylecheckaibot")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Always write to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # Write to a rotating file only in local / non-container environments
    _in_container = bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("DOCKER_ENV")
    )
    _file_logging = os.getenv("LOG_TO_FILE", "0" if _in_container else "1")
    if _file_logging == "1":
        try:
            log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            file_handler = RotatingFileHandler(
                log_dir / "bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            logger.warning("Could not open log file; file logging disabled.")

    return logger


logger = setup_logging()
