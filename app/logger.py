import logging
import os
from logging.handlers import RotatingFileHandler
from app.settings import settings


def setup_logging():
    # Logs Directory
    log_dir = settings.log_dir
    os.makedirs(log_dir, exist_ok=True)

    handlers = [
        logging.StreamHandler(),  # For Check logs with docker compose logs.
        RotatingFileHandler(
            filename=os.path.join(log_dir, "app.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding="utf-8",
        ),
    ]

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def get_logger(name: str = __name__):
    return logging.getLogger(name)
