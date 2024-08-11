import logging

LOG_FORMAT = (
    '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
    '-35s %(lineno) -5d: %(message)s'
)
LOGGER = logging.getLogger('datemaker')
formatter = logging.Formatter(LOG_FORMAT)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)
