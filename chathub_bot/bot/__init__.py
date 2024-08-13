import logging
import os


def setup_logger():
    logger = logging.getLogger(__name__)
    log_format = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(log_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


TG_TOKEN = os.getenv('TG_BOT_TOKEN', '')
MESSAGE_BROKER_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
MESSAGE_BROKER_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
MESSAGE_BROKER_VIRTUAL_HOST = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
MESSAGE_BROKER_EXCHANGE = os.getenv('TG_BOT_RABBITMQ_EXCHANGE', 'default_exchange')
MESSAGE_BROKER_QUEUE = os.getenv('TG_BOT_RABBITMQ_QUEUE', 'default_queue')
MESSAGE_BROKER_ROUTING_KEY = os.getenv(
    'TG_BOT_RABBITMQ_ROUTING_KEY',
    'default_routing_key'
)
MESSAGE_BROKER_USERNAME = os.getenv('RABBITMQ_USERNAME', 'guest')
MESSAGE_BROKER_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_DB = os.getenv('POSTGRES_DB', 'chathub')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'guest')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'guest')

LOGGER = setup_logger()
