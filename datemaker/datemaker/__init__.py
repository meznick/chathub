import logging
import os
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
    INVITE_TO_MEETING = 'invite_to_meeting'
    SEND_PARTNER_PROFILE = 'send_partner_profile'
    SEND_PARTNER_RATING_REQUEST = 'send_partner_rating_request'
    SEND_PARTNER_PROFILE_VERIFICATION_REQUEST = 'send_partner_profile_verification_request'
    SEND_FINAL_DATING_MESSAGE = 'send_final_dating_message'
    SEND_MATCH_MESSAGE = 'send_match_message'
    SEND_READY_FOR_EVENT_REQUEST = 'send_ready_for_event_request'
    SEND_BREAK_MESSAGE = 'send_break_message'


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
    SKIPPED = 5


EVENT_IDEAL_USERS = 20

BOT_VARIABLES_LOADED = os.getenv('BOT_VARIABLES_LOADED', 'false')
if BOT_VARIABLES_LOADED.lower() == 'false':
    load_dotenv(dotenv_path='/app/.env')
    logging.info(f'Environment variables loaded: {BOT_VARIABLES_LOADED}')

DEBUG = os.getenv('DEBUG', 'false')
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
MEET_CREDS_FILE = os.getenv('MEET_CREDS_FILE')
MEET_TOKEN_FILE = os.getenv('MEET_TOKEN_FILE')
# all parameters for AsyncPgConnector
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_DB = os.getenv('POSTGRES_DB', '')
POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

TG_BOT_ROUTING_KEY = 'tg_bot_dev' if DEBUG.lower() == 'true' else 'tg_bot_prod'
