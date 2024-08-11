import logging

LOG_FORMAT = (
    '[%(levelname) -6s, %(name) -10s] %(asctime)s: %(message)s'
)
LOGGER = logging.getLogger('tgbot')
formatter = logging.Formatter(LOG_FORMAT)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)
