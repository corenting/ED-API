import sys

from loguru import logger

from app import config

__version__ = "4.2.1"

logger.remove()
logger.add(sys.stderr, level=config.LOG_LEVEL)
