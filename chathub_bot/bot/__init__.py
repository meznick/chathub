import logging
import os

__version__ = '0.1.0'

from enum import Enum
from dotenv import load_dotenv


def setup_logger(name):
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


# same as datemaker/datemaker/__init__.py:22
class DateMakerCommands(Enum):
    LIST_EVENTS = 'list_events'
    REGISTER_USER_TO_EVENT = 'register_event'
    CANCEL_REGISTRATION = 'cancel_registration'
    CONFIRM_USER_EVENT_REGISTRATION = 'confirm_registration'


# same as datemaker/datemaker/__init__.py:30
class BotCommands(Enum):
    CONFIRM_USER_EVENT_REGISTRATION = 'confirm_registration'
    SEND_RULES = 'send_rules'
    INVITE_TO_MEETING = 'invite_to_meeting'
    SEND_PARTNER_PROFILE = 'send_partner_profile'
    SEND_PARTNER_RATING_REQUEST = 'send_partner_rating_request'
    SEND_PARTNER_PROFILE_VERIFICATION_REQUEST = 'send_partner_profile_verification_request'
    SEND_FINAL_DATING_MESSAGE = 'send_final_dating_message'
    SEND_MATCH_MESSAGE = 'send_match_message'
    SEND_READY_FOR_EVENT_REQUEST = 'send_ready_for_event_request'
    SEND_BREAK_MESSAGE = 'send_break_message'
    SEND_USER_WILL_TAKE_PART_IN_EVENT = 'send_user_will_take_part_in_event'
    SEND_USER_WILL_NOT_TAKE_PART_IN_EVENT = 'send_user_will_not_take_part_in_event'


BOT_VARIABLES_LOADED = os.getenv('BOT_VARIABLES_LOADED', 'false')
if BOT_VARIABLES_LOADED.lower() == 'false':
    load_dotenv(dotenv_path='/app/.env')
    logging.info(f'Environment variables loaded: {BOT_VARIABLES_LOADED}')

DEBUG = os.getenv('DEBUG', 'false')

TG_TOKEN = os.getenv('TG_BOT_TOKEN', '')
# Read RabbitMQ settings and credentials from environment
MESSAGE_BROKER_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
MESSAGE_BROKER_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
MESSAGE_BROKER_VIRTUAL_HOST = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
MESSAGE_BROKER_EXCHANGE = os.getenv('TG_BOT_RABBITMQ_EXCHANGE', '')
MESSAGE_BROKER_QUEUE = os.getenv('TG_BOT_RABBITMQ_QUEUE', '')
MESSAGE_BROKER_ROUTING_KEY = os.getenv(
    'TG_BOT_RABBITMQ_ROUTING_KEY',
    ''
)
MESSAGE_BROKER_USERNAME = os.getenv('TG_BOT_RABBITMQ_USERNAME', '')
MESSAGE_BROKER_PASSWORD = os.getenv('TG_BOT_RABBITMQ_PASSWORD', '')
# Read Postgres credentials from environment
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_DB = os.getenv('POSTGRES_DB', '')
POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
# Read AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_BUCKET = os.getenv('AWS_BUCKET', '')

DATE_MAKER_ROUTING_KEY = 'date_maker_dev' if DEBUG.lower() == 'true' else 'date_maker_prod'
