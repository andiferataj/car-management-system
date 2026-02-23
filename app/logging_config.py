import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def configure_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
