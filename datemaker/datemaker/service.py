"""
Class and setting for main class for managing date-making logic.
"""
import asyncio
import logging

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector
from datemaker import setup_logger
from .meet_api_controller import GoogleMeetApiController

# also, we probably will need connector to DB, user management, authentication
# these things already exist as separate modules in this repo

LOGGER = setup_logger(__name__)


class DateMakerService:
    # settings for controllers should be passed using env variables and read
    # inside __init__.py
    meet_api_controller: GoogleMeetApiController = None
    message_broker_controller: RabbitMQConnector = None

    def __init__(
            self,
            # all parameters from GoogleMeetApiController

            # all parameters from RabbitMQConnector (0.0.3)
            message_broker_virtual_host: str,
            message_broker_exchange: str,
            message_broker_queue: str,
            message_broker_routing_key: str,
            message_broker_username: str,
            message_broker_password: str,
            message_broker_host: str,
            message_broker_port: int,
            # all parameters for AsyncPgConnector
            postgres_host: str,
            postgres_port: int,
            postgres_db: str,
            postgres_user: str,
            postgres_password: str,
            # other
            debug: bool = False,
    ):
        self.meet_api_controller = GoogleMeetApiController()
        self.message_broker_controller = RabbitMQConnector(
            host=message_broker_host,
            port=message_broker_port,
            virtual_host=message_broker_virtual_host,
            exchange=message_broker_exchange,
            queue=message_broker_queue,
            routing_key=message_broker_routing_key,
            username=message_broker_username,
            password=message_broker_password,
            message_callback=self.process_incoming_message,
            caller_service='datemaker',
            loglevel=logging.DEBUG if debug else logging.INFO,
        )
        self.postgres_controller = AsyncPgConnector(
            host=postgres_host,
            port=postgres_port,
            db=postgres_db,
            username=postgres_user,
            password=postgres_password,
        )
        LOGGER.info('DateMaker service initialized')

    async def run(self):
        """
        Method that runs for managing date-making logic.
        Most likely, here you should only schedule regular actions: creating
        event, starting events and saving results. But please remember about
        functionality for processing incoming messages, it should be able to
        work as well. In a bad scenario you will have to create separate thread
        or make this class asynchronous or something else.
        """
        LOGGER.info('Running DateMakerService...')
        try:
            loop = asyncio.get_running_loop()
            self.message_broker_controller.run(custom_loop=loop)
            await self.postgres_controller.connect()
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            LOGGER.info('Stopping DateMakerService...')
            self.message_broker_controller.disconnect()

    def process_incoming_message(self, channel, method, properties, body):
        """
        Method for processing incoming message from RabbitMQ broker.
        Possible messages can be:
        - event registration request
        - event selection
        - event registration confirmation

        Documentation from pika:
        https://pika.readthedocs.io/en/stable/modules/channel.html?highlight=on_message_callback#pika.channel.Channel.basic_consume

        :param channel: RabbitMQ channel
        :param method: RabbitMQ method
        :param properties: message properties
        :param body: message body
        """

        # high-level logic something like this?
        user = None  # from message get info about user to respond?
        if 'registration request' in body:
            # check if user already registered?
            self.list_events(user)  # this sends available events to user
        elif 'event selection' in body:
            self.register_user_to_event(user)
        elif 'registration confirmation' in body:
            self.confirm_user_event_registration(user)

        ...

    def list_events(self, user, include_finished: bool = False, limit: int = 10):
        """
        Method for "listing" events by user request.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L46

        Method puts a message into queue for bot (or mini-app), containing
        events in a some format readable by recipient.

        :param user: On developer's decision.
        :param include_finished: Include all events in the result.
                    It can be potentially useful for debugging.
        :param limit: Limit the number of events to return.
        """
        ...

    def register_user_to_event(self, user):
        """
        Method for completing user registration request.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L46

        Method must put a success message into the queue for bot/mini-app.

        :param user: On developer's decision.
        :return:
        """

    def confirm_user_event_registration(self, user):
        """
        Method for confirmation sequence start.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L57

        Method should put messages into queue for bot (or mini-app).
        Bot/mini-app will trigger and send confirmation request to user.
        After user responds, new message will appear in incoming queue and it
        should be parsed correctly with `process_incoming_message` method.

        :param user: On developer's decision.
        """
        ...

    def generate_events(self):
        """
        This service should generate new events for users.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L64

        Now we haven’t discussed actual realization.
        """
        ...

    def run_event(self):
        """
        Method for running actual dating event.
        I'd recommend using a finite state machine pattern here.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L79
        """
        ...

    def save_event_result(self, event):
        """
        Method saves artifacts into DB.
        An actual artifact list is on developer.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L70

        :param event: Some event ID?
        """
        ...
