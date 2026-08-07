import logging
import sys
from logging.handlers import RotatingFileHandler

from backend.core.settings import settings


def setup_logging() -> logging.Logger:
    """
    Configures centralized logging for the application.
    Supports console logging and file logging depending on the environment.
    """
    logger = logging.getLogger("elhgs")
    
    # Avoid duplicating logs if setup is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (Rotating)
    file_handler = RotatingFileHandler(
        "elhgs.log", maxBytes=10485760, backupCount=5  # 10MB per file, max 5 files
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()
