from loguru import logger
import sys
from app import config

__version__ = "4.1.1"

logger.remove()
logger.add(sys.stderr, level=config.LOG_LEVEL)
