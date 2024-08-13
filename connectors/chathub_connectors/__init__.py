import logging


def setup_logger():
    logger = logging.getLogger(__name__)
    log_format = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(log_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


LOGGER = setup_logger()
