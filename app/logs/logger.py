from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging


def setup_logging() -> None:
    root_logger = logging.getLogger()

    if getattr(root_logger, "_tenet_configured", False):
        return

    Path("logs").mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    app_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        "logs/error.log",
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    root_logger._tenet_configured = True