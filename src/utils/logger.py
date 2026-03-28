from __future__ import annotations

import logging
import os

from src.utils.config import settings


def get_logger(name: str) -> logging.Logger:
    os.makedirs(os.path.dirname(settings.log_path), exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )

        file_handler = logging.FileHandler(settings.log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
