import asyncio
from asyncio import sleep, AbstractEventLoop
from datetime import timedelta, datetime

import pandas as pd

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector
from datemaker import (
    setup_logger,
    EventStateIDs,
    BotCommands,
)
from .intelligent_agent import IntelligentAgent
from .meet_api_controller import GoogleMeetApiController

LOGGER = setup_logger(__name__)


class RegistrationConfirmationRunner:
    """
    Class that encapsulates logic for running preparation for an event.
    """

    def __init__(
            self,
            event_id: int,
            start_time: datetime,
            meet_api_controller: GoogleMeetApiController,
            postgres_controller: AsyncPgConnector,
            rabbitmq_controller: AIORabbitMQConnector,
            custom_event_loop: AbstractEventLoop = None,
    ):
        self.event_id = event_id
        self.event_start_time = start_time
        self.meet_api = meet_api_controller
        self.postgres = postgres_controller
        self.rabbitmq = rabbitmq_controller
        self.running = False
        self.registrations = []
        loop = custom_event_loop or asyncio.get_event_loop()
        self.intelligence_agent = IntelligentAgent(loop, postgres_controller)
        LOGGER.info(f'RegistrationConfirmationRunner for event#{event_id} initialized')

    async def handle_preparations(self):
        LOGGER.info(f'Registration confirmation for event#{self.event_id} has started')
        self.running = True
        await self.set_event_state(EventStateIDs.REGISTRATION_CONFIRMATION)
        await self.collect_registrations()
        await self.trigger_bot_command(BotCommands.CONFIRM_USER_EVENT_REGISTRATION)
        await self.wait_for_confirmations()
        await self.generate_user_groups()
        await self.set_event_state(EventStateIDs.READY)
        LOGGER.info(f'Registration confirmation for event#{self.event_id} has finished')

    async def set_event_state(self, state: EventStateIDs):
        await self.postgres.set_event_state(self.event_id, state.value)

    async def collect_registrations(self):
        """
        Collecting all users registered for event.
        """
        LOGGER.info(f'Collecting registrations for event#{self.event_id}')
        self.registrations = await self.postgres.get_event_registrations(self.event_id)

    async def trigger_bot_command(self, command: BotCommands):
        for user in self.registrations:
            await self.rabbitmq.publish(
                message=command.value,
                routing_key='tg_bot_dev',
                exchange='chathub_direct_main',
                headers={
                    'user_id': user.get('user_id'),
                    'chat_id': user.get('user_id'),
                    'event_id': self.event_id,
                }
            )
        LOGGER.info(f'Command {command} triggered for {len(self.registrations)} users')

    async def wait_for_confirmations(self):
        is_all_confirmed = False  # all users confirmed registrations
        is_timeout = False        # confirmation time is out (1 hour before event)
        while not (is_all_confirmed or is_timeout):
            LOGGER.debug(f'Waiting confirmations for event {self.event_id}')
            await sleep(100)
            is_timeout = self.event_start_time - datetime.now() < timedelta(hours=1)
            self.registrations = await self.postgres.get_event_registrations(self.event_id)
            is_all_confirmed = len(
                {user.get('user_id') for user in self.registrations} -
                {user.get('user_id') for user in self.registrations if user.get('confirmed_on_dttm')}
            ) == 0
        LOGGER.debug(
            f'All users confirmed registration: {is_all_confirmed}, '
            f'timeout: {is_timeout} '
            f'for event#{self.event_id}'
        )
        LOGGER.info(f'Waiting for confirmation ended for event#{self.event_id}')

    async def generate_user_groups(self):
        """
        When confirmed users collected -- splitting them into groups according
        to maximize dating experience.

        The result of this method should be a list of users, split into groups.
        In each group, there should be prepared tuple: user pairs that date each
        other.
        """
        LOGGER.debug(f'Generating user groups for event#{self.event_id}')
        # collect user data to make groups
        confirmed_user_ids = {
            user.get('user_id') for user in self.registrations if user.get('confirmed_on_dttm')
        }
        LOGGER.debug(f'Got {len(confirmed_user_ids)} confirmed users for event#{self.event_id}')
        confirmed_users = []
        for user_id in confirmed_user_ids:
            confirmed_users.append(
                await self.postgres.get_user(user_id)
            )

        df_registrations = pd.DataFrame(
            self.registrations,
            columns=['user_id', 'registered_on_dttm', 'confirmed_on_dttm'],
        )
        df_users = pd.DataFrame(
            confirmed_users,
            columns=[
                'user_id',
                'username',
                'password_hash',
                'bio',
                'birthday',
                'sex',
                'name',
                'city',
                'rating',
                'manual_score',
            ]
        )
        df_users = df_users.merge(df_registrations, on='user_id')

        self.intelligence_agent.cluster_users_for_event(df_users, self.event_id)
        LOGGER.info(f'Generated user groups for event#{self.event_id}')
