import logging
import os


def setup_logger(name: str, log_level: int = logging.DEBUG):
    logger = logging.getLogger(name)

    log_format = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    debug = os.getenv('DEBUG', 'false')

    level = logging.DEBUG if debug.lower() == 'true' else logging.INFO
    logger.setLevel(level)
    stream_handler.setLevel(level)
    return logger
