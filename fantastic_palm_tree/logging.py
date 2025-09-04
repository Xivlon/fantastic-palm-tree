import logging
from typing import Optional


_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str = "fantastic_palm_tree") -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            handler.setFormatter(logging.Formatter(fmt))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        _LOGGER = logger
    return _LOGGER
