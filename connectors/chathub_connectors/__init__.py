import logging
import os


def setup_logger(name: str, log_level: int = logging.DEBUG):
    logger = logging.getLogger(name)

    # Only add handler if the logger doesn't already have handlers
    if not logger.handlers:
        log_format = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
        formatter = logging.Formatter(log_format)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Set propagate to False to prevent duplicate logs
        logger.propagate = False

    debug = os.getenv('DEBUG', 'false')

    level = logging.DEBUG if debug.lower() == 'true' else logging.INFO
    logger.setLevel(level)

    # Only set handler level if we added a handler
    if logger.handlers:
        logger.handlers[0].setLevel(level)

    return logger
