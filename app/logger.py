import logging
from app.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name: str = __name__):
    return logging.getLogger(name)
