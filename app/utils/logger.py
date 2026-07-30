import logging
import sys

from app.core.config import settings


def setup_logging(log_level: str | None = None) -> None:
    level = log_level or settings.LOG_LEVEL
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s <|> %(levelname)s <|> %(name)s <|> %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
