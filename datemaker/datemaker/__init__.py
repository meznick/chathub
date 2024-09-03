import logging
import os


def setup_logger(name):
    logger = logging.getLogger(name)

    log_format = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    debug = os.getenv('DEBUG', 'false')

    logger.setLevel(logging.DEBUG if debug.lower() == 'true' else logging.INFO)
    return logger


# same as chathub_bot/bot/__init__.py:23
DATE_MAKER_COMMANDS = {
    'list_events': 'list_events',
    'register_user_to_event': 'register_event',
    'confirm_user_event_registration': 'confirm_registration',
}

# all parameters from RabbitMQConnector (0.0.3)
MESSAGE_BROKER_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
MESSAGE_BROKER_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
MESSAGE_BROKER_VIRTUAL_HOST = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
MESSAGE_BROKER_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'default_exchange')
MESSAGE_BROKER_QUEUE = os.getenv('DATEMAKER_RABBITMQ_QUEUE', 'default_queue')
MESSAGE_BROKER_ROUTING_KEY = os.getenv(
    'DATEMAKER_RABBITMQ_ROUTING_KEY',
    'default_routing_key'
)
MESSAGE_BROKER_USERNAME = os.getenv('DATEMAKER_RABBITMQ_USERNAME', 'guest')
MESSAGE_BROKER_PASSWORD = os.getenv('DATEMAKER_RABBITMQ_PASSWORD', 'guest')
# all parameters from GoogleMeetApiController

# all parameters for AsyncPgConnector
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_DB = os.getenv('POSTGRES_DB', '')
POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
