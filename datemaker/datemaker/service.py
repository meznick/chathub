import asyncio
import json
from asyncio import sleep
from datetime import datetime

import aio_pika
from tzlocal import get_localzone

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector
from datemaker import (
    setup_logger,
    DateMakerCommands,
    EventStates,
    DEBUG, TG_BOT_ROUTING_KEY, MESSAGE_BROKER_EXCHANGE
)
from .dating_event_runner import DateRunner
from .meet_api_controller import GoogleMeetApiController
from .registration_confirmation_runner import RegistrationConfirmationRunner

LOGGER = setup_logger(__name__)


class DateMakerService:
    """
    Class for managing date-making logic.
    """
    def __init__(
            self,
            # all parameters from GoogleMeetApiController
            meet_creds_file: str,
            meet_token_file: str,
            # all parameters from RabbitMQConnector (0.0.3)
            message_broker_virtual_host: str,
            message_broker_exchange: str,
            message_broker_queue: str,
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
        self.debug = debug
        self.message_broker_queue = message_broker_queue
        self.message_broker_exchange = message_broker_exchange
        self.meet_api_controller = GoogleMeetApiController(
            creds_file_path=meet_creds_file,
            token_file_path=meet_token_file,
        )
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
        LOGGER.info(f'DateMaker service initialized. Debug: {self.debug}')

    async def run(self):
        """
        Method that runs for managing date-making logic.
        Most likely, here you should only schedule regular actions: creating
        an event, starting events, saving results.
        Please remember about
        functionality for processing incoming messages - it should be able to
        work as well.
        In a bad scenario you will have to create a separate thread
        or make this class asynchronous or something else.
        """
        LOGGER.info('Running DateMakerService...')
        try:
            await self.async_pg_controller.connect()
            await self.async_rmq_controller.connect()
            await self.async_rmq_controller.listen_queue(
                queue_name=self.message_broker_queue,
                callback=self.process_incoming_message
            )
            self.meet_api_controller.connect()
            await self.run_date_making()
        except KeyboardInterrupt:
            LOGGER.info('Stopping DateMakerService...')

    async def process_incoming_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        """
        Method for processing an incoming message from RabbitMQ broker.
        Possible messages can be:
        - event registration request
        - event selection
        - event registration confirmation

        :param message: Incoming message object.
        """
        headers = message.headers
        channel_number = message.channel.number
        message = message.body.decode('utf-8')

        LOGGER.debug(
            f'Got message on channel {channel_number}: {message}. '
            f'Headers: {headers}.'
        )
        try:
            user = await self.async_pg_controller.get_user(int(headers.get('user_id', -1)))
            if not user:
                raise Exception('No user found')

            await self.process_commands(message, headers, user)

        except Exception as e:
            LOGGER.error(
                f'Error in processing message "{message}" '
                f'with params {headers} '
                f'Error: {e}'
            )
            await self.async_rmq_controller.publish(
                json.dumps({'success': False}),
                routing_key=TG_BOT_ROUTING_KEY,
                exchange=MESSAGE_BROKER_EXCHANGE,
                headers=headers
            )

    async def process_commands(self, message, message_params, user):
        if DateMakerCommands.LIST_EVENTS.value in message:
            await self.list_events(user, message_params)

        elif DateMakerCommands.REGISTER_USER_TO_EVENT.value in message:
            event_id = message_params.get('event_id', None)
            if not event_id:
                LOGGER.error(
                    f'No event_id got with registration request for user {user}: {message}'
                )
            await self.register_user_to_event(user, message_params)

        elif DateMakerCommands.CONFIRM_USER_EVENT_REGISTRATION.value in message:
            event_id = message_params.get('event_id', None)
            if not event_id:
                LOGGER.error(
                    f'No event_id got with registration confirmation for user {user}: {message}'
                )
            await self.confirm_user_event_registration(user, message_params)

        elif DateMakerCommands.CANCEL_REGISTRATION.value in message:
            event_id = int(message_params.get('event_id', -1))
            if event_id != 0:
                await self.cancel_event_registration(user, message_params)
            elif event_id == 0:
                events = await self.async_pg_controller.get_event_registrations_for_user(user)
                for event_id in [event['event_id'] for event in events]:
                    message_params.update({'event_id': event_id})
                    await self.cancel_event_registration(user, message_params)
            else:
                LOGGER.error(
                    f'No event_id got with registration cancellation for user {user}: {message}'
                )

    async def list_events(self, user, message_params: dict):
        """
        Method for "listing" events by user request.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L46

        Method puts a message into queue for bot (or mini-app), containing
        events in a some format readable by recipient.

        :param user: Database user object.
        :param message_params: Dictionary of received parameters.
        """
        events = await self.async_pg_controller.get_dating_events(timezone='Europe/Moscow')
        events_list = [
            {
                event.get('id'): {
                    'start_time': event.get('start_dttm').strftime('%Y-%m-%d %H:%M:%S'),
                    'users_limit': event.get('users_limit'),
                }
            } for event in events
        ]
        await self.async_rmq_controller.publish(
            json.dumps(events_list),
            routing_key=TG_BOT_ROUTING_KEY,
            exchange=MESSAGE_BROKER_EXCHANGE,
            headers=message_params
        )

    async def register_user_to_event(self, user, message_params: dict):
        """
        Method for completing a user registration request.
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L46

        Method must put a success message into the queue for bot/mini-app.

        :param message_params: Dictionary of received parameters.
        :param user: Database user object.
        :return:
        """
        event_id = int(message_params['event_id'])
        is_registered = False

        event_registrations = await self.async_pg_controller.get_event_registrations(
            event_id
        )

        registered_users = [
            user.get('user_id') for user in event_registrations
        ]

        if user.get('id') not in registered_users:
            await self.async_pg_controller.register_for_event(
                user=user,
                event_id=event_id
            )
            is_registered = True

        result = {
            'user_registered': is_registered
        }
        await self.async_rmq_controller.publish(
            json.dumps(result),
            routing_key=TG_BOT_ROUTING_KEY,
            exchange=MESSAGE_BROKER_EXCHANGE,
            headers=message_params
        )

    async def confirm_user_event_registration(
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

        event_registrations = await self.async_pg_controller.get_event_registrations(
            event_id
        )

        registered_users = [
            user.get('user_id') for user in event_registrations
        ]

        if user.get('id') in registered_users:
            await self.async_pg_controller.confirm_registration(
                user=user,
                event_id=event_id
            )
            is_confirmed = True

        result = {
            'registration_confirmed': is_confirmed
        }
        await self.async_rmq_controller.publish(
            json.dumps(result),
            routing_key=TG_BOT_ROUTING_KEY,
            exchange=MESSAGE_BROKER_EXCHANGE,
            headers=message_params
        )

    async def cancel_event_registration(self, user, message_params: dict):
        event_id = int(message_params['event_id'])
        is_cancelled = False
        event_registrations = await self.async_pg_controller.get_event_registrations(
            event_id
        )
        registered_users = [
            user.get('user_id') for user in event_registrations
        ]

        if user.get('id') in registered_users:
            await self.async_pg_controller.cancel_registration(
                user=user,
                event_id=event_id
            )
            is_cancelled = True

        result = {'registration_cancelled': is_cancelled}
        await self.async_rmq_controller.publish(
            json.dumps(result),
            routing_key=TG_BOT_ROUTING_KEY,
            exchange=MESSAGE_BROKER_EXCHANGE,
            headers=message_params
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
        if not DEBUG:
            await sleep(10)
        while True:
            events = await self._collect_events()
            await self._process_events(events, loop)
            await sleep(59)

    async def _process_events(self, events, loop):
        # for event in events create processor and run
        if events:
            LOGGER.debug('Processing events')
        for event in events:
            if event.get('state_name') == EventStates.READY.value:
                runner = DateRunner(
                    event_id=event.get('id'),
                    start_time=event.get('start_dttm'),
                    meet_api_controller=self.meet_api_controller,
                    postgres_controller=self.async_pg_controller,
                    rabbitmq_controller=self.async_rmq_controller,
                    custom_event_loop=loop,
                    debug=self.debug,
                )
                loop.create_task(runner.run_event())
                loop.create_task(runner.save_event_results())
            elif event.get('state_name') == EventStates.NOT_STARTED.value:
                runner = RegistrationConfirmationRunner(
                    event_id=event.get('id'),
                    start_time=event.get('start_dttm'),
                    meet_api_controller=self.meet_api_controller,
                    postgres_controller=self.async_pg_controller,
                    rabbitmq_controller=self.async_rmq_controller,
                    custom_event_loop=loop,
                    debug=self.debug,
                )
                loop.create_task(runner.handle_preparations())

    async def _collect_events(self):
        """
        Collect events to process: registration confirmations and dating events.
        :return:
        """
        LOGGER.debug('Collecting events')
        events = await self.async_pg_controller.get_dating_events(
            limit=10,
            timezone=get_localzone(),
        )
        dating_events = [
            e
            for e
            in events
            if (
                # ready to start
                e.get('state_name', '') == EventStates.READY.value and
                # should start in 5 minutes
                e.get('start_dttm') - datetime.now() < DateRunner.send_rules_offset
            )
        ]
        confirmations = [
            e
            for e
            in events
            if (
                # ready to process
                e.get('state_name', '') == EventStates.NOT_STARTED.value and
                # starts tomorrow - registration should start 1 day before the event starts
                e.get('start_dttm') - datetime.now() <
                RegistrationConfirmationRunner.registration_timeout_offset
            )
        ]
        events = dating_events + confirmations
        if len(events):
            LOGGER.info(
                f'Got {len(events)} ({len(dating_events)} events + '
                f'{len(confirmations)} confirmations) events to process'
            )
        else:
            LOGGER.debug(
                f'Got {len(events)} ({len(dating_events)} + {len(confirmations)}) events to process'
            )
        return events
