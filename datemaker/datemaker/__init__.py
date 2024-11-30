import logging
import os
from enum import Enum


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


# same as chathub_bot/bot/__init__.py:25
class DateMakerCommands(Enum):
    LIST_EVENTS = 'list_events'
    REGISTER_USER_TO_EVENT = 'register_event'
    CANCEL_REGISTRATION = 'cancel_registration'
    CONFIRM_USER_EVENT_REGISTRATION = 'confirm_registration'


# same as chathub_bot/bot/__init__.py:33
class BotCommands(Enum):
    CONFIRM_USER_EVENT_REGISTRATION = 'confirm_registration'
    SEND_RULES = 'send_rules'


class EventStates(Enum):
    NOT_STARTED = 'NOT_STARTED'                 # 0
    REGISTRATION_CONFIRMATION = 'REG_CONFIRM'   # 1
    READY = 'READY'                             # 2
    RUNNING = 'RUNNING'                         # 3
    FINISHED = 'FINISHED'                       # 4


class EventStateIDs(Enum):
    NOT_STARTED = 0
    REGISTRATION_CONFIRMATION = 1
    READY = 2
    RUNNING = 3
    FINISHED = 4


EVENT_IDEAL_USERS = 20


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
