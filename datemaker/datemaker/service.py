"""
Class and setting for the main class for managing date-making logic.
"""
import asyncio
import copy
import json
import logging
from asyncio import sleep
from datetime import timedelta
from typing import List

from pika.spec import BasicProperties

from chathub_connectors.postgres_connector import PostgresConnection, AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector, AIORabbitMQConnector
from datemaker import setup_logger, DateMakerCommands, EventStates
from .meet_api_controller import GoogleMeetApiController

# also, we probably will need connector to DB, user management, authentication
# these things already exist as separate modules in this repo

LOGGER = setup_logger(__name__)


class DatingFSM:
    """
    Finite state machine for performing dating event.
    States:
        - initial (waiting for all users, see dating event documentation: 2)
        - dating
        - break (dating event documentation: 4)
        - final (dating event documentation: 6)
        Transitions:
        - initial -> dating
        - dating -> break
        - break -> dating
        - dating -> final
    """
    def __init__(self, group):
        """
        :param group: Group of users that will be dating.
        """
        ...

    async def run(self):
        ...


class DateRunner:
    """
    Class that encapsulates logic for running singe date event.
    """
    def __init__(
            self,
            event_id: int,
            meet_api_controller: GoogleMeetApiController,
            postgres_controller: AsyncPgConnector,
            rabbitmq_controller: AIORabbitMQConnector,
    ):
        self.event_id = event_id
        self.meet_api = meet_api_controller
        self.postgres = postgres_controller
        self.rabbitmq = rabbitmq_controller
        self.running = False
        self.groups: List = []  # data collected from RegistrationConfirmationRunner
        LOGGER.info(f'DateRunner for event#{event_id} initialized')

    async def run_event(self):
        """
        Method for running actual dating event.
        I'd recommend using a finite state machine pattern here.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L79
        """
        LOGGER.info(f'Dating event#{self.event_id} has started')
        self.running = True
        await self.set_event_state(EventStates.RUNNING)
        await self.trigger_bot_to_send_rules()
        await self.get_event_prepared_data()
        for group in self.groups:
            await self.run_dating_fsm(group)
        # wait for all groups to finish and then set state to FINISHED
        LOGGER.info(f'Dating event#{self.event_id} has finished')

    async def set_event_state(self, state: EventStates):
        ...

    async def trigger_bot_to_send_rules(self):
        ...

    async def get_event_prepared_data(self):
        """
        Collecting prepared data: dating groups and pairs.
        """
        ...

    async def run_dating_fsm(self, group):
        """
        Running FSM that handles dating process.
        """
        loop = asyncio.get_running_loop()
        loop.create_task(
            DatingFSM(group).run()
        )

    async def save_event_results(self):
        while self.running:
            await sleep(100)
        LOGGER.debug(f'Saving event results for event#{self.event_id}')


class RegistrationConfirmationRunner:
    def __init__(
            self,
            event_id: int,
            meet_api_controller: GoogleMeetApiController,
            postgres_controller: AsyncPgConnector,
            rabbitmq_controller: AIORabbitMQConnector,
    ):
        self.event_id = event_id
        self.meet_api = meet_api_controller
        self.postgres = postgres_controller
        self.rabbitmq = rabbitmq_controller
        self.running = False
        LOGGER.info(f'RegistrationConfirmationRunner for event#{event_id} initialized')

    async def handle_preparations(self):
        LOGGER.info(f'Registration confirmation for event#{self.event_id} has started')
        self.running = True
        await self.set_event_state(EventStates.REGISTRATION_CONFIRMATION)
        await self.collect_registrations()
        await self.trigger_bot_to_send_confirmation_requests()
        await self.generate_user_groups()
        await self.set_event_state(EventStates.READY)
        LOGGER.info(f'Registration confirmation for event#{self.event_id} has finished')

    async def set_event_state(self, state: EventStates):
        ...

    async def collect_registrations(self):
        """
        Collecting all users registered for event.
        """
        LOGGER.debug(f'Collecting registrations for event#{self.event_id}')

    async def trigger_bot_to_send_confirmation_requests(self):
        """
        To participate in event users should send confirmation.
        :return:
        """

    async def generate_user_groups(self):
        """
        When confirmed users collected -- splitting them into groups according
        to maximize dating experience.

        The result of this method should be a list of users, split into groups.
        In each group, there should be prepared tuple: user pairs that date each
        other.
        """
        LOGGER.debug(f'Generating user groups for event#{self.event_id}')


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
        # self.meet_api_controller = GoogleMeetApiController()
        # LEGACY CONTROLLER, TO BE REMOVED
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
        # LEGACY CONTROLLER, TO BE REMOVED
        self.postgres_controller = PostgresConnection(
            host=postgres_host,
            port=postgres_port,
            db=postgres_db,
            username=postgres_user,
            password=postgres_password,
        )
        # NEW CONTROLLERS, NOW USE ONLY FOR PASSING INTO DATING RUNNER CLASSES
        self.async_pg_controller = AsyncPgConnector(
            host=postgres_host,
            port=postgres_port,
            db=postgres_db,
            username=postgres_user,
            password=postgres_password,
        )
        self.async_rmq_controller = AIORabbitMQConnector(
            host=message_broker_host,
            port=message_broker_port,
            virtual_host=message_broker_virtual_host,
            exchange=message_broker_exchange,
            username=message_broker_username,
            password=message_broker_password,
            caller_service='datemaker',
        )
        LOGGER.info('DateMaker service initialized')

    def run(self):
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
            loop = asyncio.get_event_loop()
            self.message_broker_controller.connect()
            self.postgres_controller.connect()
            loop.create_task(self.run_date_making())
            loop.run_forever()
        except KeyboardInterrupt:
            LOGGER.info('Stopping DateMakerService...')
            self.message_broker_controller.disconnect()
            self.postgres_controller.disconnect()

    def process_incoming_message(self, channel, method, properties, body):
        """
        Method for processing a incoming message from RabbitMQ broker.
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
        LOGGER.debug(
            f'Got message on channel {channel.channel_number}: {body}. '
            f'Method: {method}. Headers: {properties.headers}.'
        )
        # properties should contain data to return answer to right user:
        # - chat id (from tg bot)?
        # user should be in headers as well, because its ID is necessary for processing
        message_params = properties.headers
        message = body.decode('utf-8')
        try:
            user = self.postgres_controller.get_user(int(message_params['user_id']))
            if not user:
                raise Exception('No user found')

            if DateMakerCommands.LIST_EVENTS.value in message:
                self.list_events(user, message_params)

            elif DateMakerCommands.REGISTER_USER_TO_EVENT.value in message:
                event_id = message_params.get('event_id', None)
                if not event_id:
                    LOGGER.error(
                        f'No event_id got with registration request for user {user}: {message}'
                    )
                self.register_user_to_event(user, message_params)

            elif DateMakerCommands.CONFIRM_USER_EVENT_REGISTRATION.value in message:
                event_id = message_params.get('event_id', None)
                if not event_id:
                    LOGGER.error(
                        f'No event_id got with registration confirmation for user {user}: {message}'
                    )
                self.confirm_user_event_registration(user, message_params)

            elif DateMakerCommands.CANCEL_REGISTRATION.value in message:
                event_id = int(message_params.get('event_id', -1))
                if event_id != 0:
                    self.cancel_event_registration(user, message_params)
                elif event_id == 0:
                    events = self.postgres_controller.get_event_registrations_for_user(user)
                    for event_id in [event['event_id'] for event in events]:
                        message_params.update({'event_id': event_id})
                        self.cancel_event_registration(user, message_params)
                else:
                    LOGGER.error(
                        f'No event_id got with registration cancellation for user {user}: {message}'
                    )

        except Exception as e:
            LOGGER.error(
                f'Error in processing message "{message}" '
                f'with params {message_params} '
                f'from {method.routing_key}. '
                f'Error: {e}'
            )
            self.message_broker_controller.publish(
                json.dumps({'success': False}),
                routing_key='tg_bot_dev',
                exchange='chathub_direct_main',
                properties=BasicProperties(headers=message_params)
            )

    def list_events(self, user, message_params: dict):
        """
        Method for "listing" events by user request.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L46

        Method puts a message into queue for bot (or mini-app), containing
        events in a some format readable by recipient.

        :param user: Database user object.
        :param message_params: Dictionary of received parameters.
        """
        events = self.postgres_controller.get_dating_events()
        events_list = [
            {
                event.get('id'): {
                    'start_time': event.get('start_dttm').strftime('%Y-%m-%d %H:%M:%S'),
                    'users_limit': event.get('users_limit'),
                }
            } for event in events
        ]
        self.message_broker_controller.publish(
            json.dumps(events_list),
            routing_key='tg_bot_dev',
            exchange='chathub_direct_main',
            properties=BasicProperties(headers=message_params)
        )

    def register_user_to_event(self, user, message_params: dict):
        """
        Method for completing user registration request.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L46

        Method must put a success message into the queue for bot/mini-app.

        :param message_params: Dictionary of received parameters.
        :param user: Database user object.
        :return:
        """
        event_id = int(message_params['event_id'])
        is_registered = False

        event_registrations = self.postgres_controller.get_event_registrations(
            event_id
        )

        registered_users = [
            user.get('user_id') for user in event_registrations
        ]

        if user.get('id') not in registered_users:
            self.postgres_controller.register_for_event(
                user=user,
                event_id=event_id
            )
            is_registered = True

        result = {
            'user_registered': is_registered
        }
        self.message_broker_controller.publish(
            json.dumps(result),
            routing_key='tg_bot_dev',
            exchange='chathub_direct_main',
            properties=BasicProperties(headers=message_params)
        )

    def confirm_user_event_registration(
            self,
            user,
            message_params: dict,
    ):
        """
        Method for confirmation sequence start.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L57

        Method should put messages into queue for bot (or mini-app).
        Bot/mini-app will trigger and send confirmation request to user.
        After user responds, new message will appear in incoming queue and it
        should be parsed correctly with `process_incoming_message` method.

        :param message_params:
        :param user: On developer's decision.
        """
        event_id = int(message_params['event_id'])
        is_confirmed = False

        event_registrations = self.postgres_controller.get_event_registrations(
            event_id
        )

        registered_users = [
            user.get('id') for user in event_registrations
        ]

        if user.get('id') in registered_users:
            self.postgres_controller.confirm_registration(
                user=user,
                event_id=event_id
            )
            is_confirmed = True

        result = {
            'registration_confirmed': is_confirmed
        }
        self.message_broker_controller.publish(
            json.dumps(result),
            routing_key='tg_bot_dev',
            exchange='chathub_direct_main',
            properties=BasicProperties(headers=message_params)
        )

    def cancel_event_registration(self, user, message_params: dict):
        event_id = int(message_params['event_id'])
        is_cancelled = False
        event_registrations = self.postgres_controller.get_event_registrations(
            event_id
        )
        registered_users = [
            user.get('user_id') for user in event_registrations
        ]

        if user.get('id') in registered_users:
            self.postgres_controller.cancel_registration(
                user=user,
                event_id=event_id
            )
            is_cancelled = True

        result = {'registration_cancelled': is_cancelled}
        self.message_broker_controller.publish(
            json.dumps(result),
            routing_key='tg_bot_dev',
            exchange='chathub_direct_main',
            properties=BasicProperties(headers=message_params)
        )

    def generate_events(self):
        """
        This service should generate new events for users.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L64

        Now we haven’t discussed actual realization.
        """
        ...

    async def run_date_making(self):
        """
        Managing dating routines:
        - checking event schedule
        - managing DateRunner instances
        """
        loop = asyncio.get_running_loop()
        while True:
            events = await self._collect_events()
            await self._process_events(events, loop)
            await sleep(59)

    async def _process_events(self, events, loop):
        # for event in events create processor and run
        LOGGER.debug('Processing events')
        for event in events:
            if event.get('state_name') == EventStates.READY:
                runner = DateRunner(
                    event_id=event['id'],
                    meet_api_controller=self.meet_api_controller,
                    postgres_controller=self.async_pg_controller,
                    rabbitmq_controller=self.async_rmq_controller,
                )
                loop.create_task(runner.run_event())
                loop.create_task(runner.save_event_results())
                # when done -- delete instance
            elif event.get('state_name') == EventStates.NOT_STARTED:
                runner = RegistrationConfirmationRunner(
                    event_id=event['id'],
                    meet_api_controller=self.meet_api_controller,
                    postgres_controller=self.async_pg_controller,
                    rabbitmq_controller=self.async_rmq_controller,
                )
                loop.create_task(runner.handle_preparations())
                # when done -- delete instance

    async def _collect_events(self):
        """
        Collect events to process: registration confirmations and dating events.
        :return:
        """
        LOGGER.debug('Collecting events')
        dating_events = [
            e
            for e
            in self.postgres_controller.get_dating_events(limit=10)
            if e.get('state_name', '') == EventStates.READY.value
        ]
        confirmations = [
            e
            for e
            in self.postgres_controller.get_dating_events(limit=10)
            if e.get('state_name', '') == EventStates.NOT_STARTED.value
        ]
        # registration should start 1 day before the event starts
        for event in confirmations:
            event['start_dttm'] = event.get('start_dttm') - timedelta(days=1)
        events = dating_events + confirmations
        LOGGER.debug(f'Got {len(events)} events to process')
        return events

    def save_event_result(self, event):
        """
        Method saves artifacts into DB.
        An actual artifact list is on developer.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L70

        :param event: Some event ID?
        """
        ...
