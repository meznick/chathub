import asyncio
from asyncio import sleep, AbstractEventLoop
from datetime import timedelta, datetime

import pandas as pd

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector
from datemaker import (
    setup_logger,
    EventStateIDs,
    BotCommands, TG_BOT_ROUTING_KEY, DEBUG, DEFAULT_EVENT_IDEAL_USERS,
)
from .intelligent_agent import IntelligentAgent
from .meet_api_controller import GoogleMeetApiController

LOGGER = setup_logger(__name__)


class RegistrationConfirmationRunner:
    """
    Class that encapsulates logic for running preparation for an event.
    """
    registration_timeout_offset = timedelta(days=1)
    confirmation_timeout_offset = (
        timedelta(seconds=1) if DEBUG.lower() == 'true' else timedelta(hours=1)
    )

    def __init__(
            self,
            event_id: int,
            start_time: datetime,
            meet_api_controller: GoogleMeetApiController,
            postgres_controller: AsyncPgConnector,
            rabbitmq_controller: AIORabbitMQConnector,
            custom_event_loop: AbstractEventLoop = None,
            debug: bool = False,
    ):
        self.event_id = event_id
        self.event_start_time = start_time
        self.meet_api = meet_api_controller
        self.postgres = postgres_controller
        self.rabbitmq = rabbitmq_controller
        self.running = False
        self.debug = debug
        self.registrations = []
        self.users_limit = DEFAULT_EVENT_IDEAL_USERS
        loop = custom_event_loop or asyncio.get_event_loop()
        self.intelligence_agent = IntelligentAgent(loop, postgres_controller, debug=self.debug)
        self.registration_end_dttm = (
                self.event_start_time - self.confirmation_timeout_offset
        )
        LOGGER.info(
            f'RegistrationConfirmationRunner for event#{event_id} initialized. '
            f'This event starts at {start_time}. '
            f'Registration will finish at {self.registration_end_dttm}.'
            f'Debug mode: {self.debug}'
        )

    async def handle_preparations(self):
        LOGGER.info(f'Registration confirmation for event#{self.event_id} has started')
        self.running = True
        await self.set_event_state(EventStateIDs.REGISTRATION_CONFIRMATION)
        await self.wait_for_confirmations()
        await self.generate_user_groups()
        await self.notify_users_registration_complete()
        await self.set_event_state(EventStateIDs.READY)
        LOGGER.info(f'Registration confirmation for event#{self.event_id} has finished')

    async def set_event_state(self, state: EventStateIDs):
        await self.postgres.set_event_state(self.event_id, state.value)

    async def trigger_bot_command(self, command: BotCommands, users: list):
        for user in users:
            await self.rabbitmq.publish(
                message=command.value,
                routing_key=TG_BOT_ROUTING_KEY,
                exchange='chathub_direct_main',
                headers={
                    'user_id': user.get('user_id'),
                    'chat_id': user.get('user_id'),
                    'event_id': self.event_id,
                }
            )
        if users:
            LOGGER.debug(f'Command {command} triggered for {len(users)} users')

    async def wait_for_confirmations(self):
        is_all_confirmed = False  # all users confirmed registrations
        is_timeout = False        # confirmation time is out (1 hour before event)
        await self._update_registrations_list()
        while not is_timeout:  # original is_all_confirmed or is_timeout - rework later
            LOGGER.debug(f'Waiting confirmations for event {self.event_id}')
            await sleep(60)
            is_timeout = self.event_start_time - self.confirmation_timeout_offset < datetime.now()
            await self._update_registrations_list()
            is_all_confirmed = len(
                {user.get('user_id') for user in self.registrations} -
                {user.get('user_id') for user in self.registrations if user.get('confirmed_on_dttm')}
            ) == 0 and len(self.registrations) > 0
        LOGGER.debug(
            f'All users confirmed registration: {is_all_confirmed}, '
            f'timeout: {is_timeout} '
            f'for event#{self.event_id}'
        )
        LOGGER.info(f'Waiting for confirmation ended for event#{self.event_id}')

    async def _update_registrations_list(self):
        LOGGER.debug(f'Updating registrations list for event#{self.event_id}')
        self.registrations = await self.postgres.get_event_registrations(self.event_id)
        confirmation_not_sent_users = [
            user for user in self.registrations if not user.get('confirmation_event_sent')
        ]
        if len(confirmation_not_sent_users):
            LOGGER.debug(
                f'Sending invites to {len(confirmation_not_sent_users)} '
                f'users for event#{self.event_id}'
            )
            await self.trigger_bot_command(
                BotCommands.CONFIRM_USER_EVENT_REGISTRATION,
                confirmation_not_sent_users
            )
            LOGGER.debug(f'Saving confirmation sent for event#{self.event_id} users to db')
            await self.postgres.save_event_confirmation_sent(
                event_id=self.event_id,
                user_ids=[uid.get('user_id') for uid in confirmation_not_sent_users]
            )

    async def generate_user_groups(self):
        """
        When confirmed users collected -- splitting them into groups according
        to maximize dating experience.

        The result of this method should be a list of users, split into groups.
        In each group, there should be prepared tuple: user pairs that date each
        other.
        """
        event_data = await self.postgres.get_dating_events(
            event_id=self.event_id,
            include_finished=True
        )
        self.users_limit = event_data[0]["users_limit"]
        LOGGER.debug(
            f'Generating user groups for event#{self.event_id}. '
            f'Max users in group: {self.users_limit}'
        )
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
            columns=['user_id', 'registered_on_dttm', 'confirmed_on_dttm', 'confirmation_event_sent'],
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

        self.intelligence_agent.cluster_users_for_event(df_users, self.event_id, self.users_limit)
        LOGGER.info(f'Generated user groups for event#{self.event_id}')

    async def notify_users_registration_complete(self):
        await sleep(10)
        LOGGER.debug(f'Notifying users that registration for event#{self.event_id} is complete')
        confirmed_user_ids = {
            user.get('user_id') for user in self.registrations if user.get('confirmed_on_dttm')
        }
        match_maked_users = {
            row.get('user_id') for row in
            await self.postgres.get_event_participants(event_id=self.event_id)
        }
        not_match_maked_users = confirmed_user_ids - match_maked_users
        await self.trigger_bot_command(
            BotCommands.SEND_USER_WILL_TAKE_PART_IN_EVENT,
            [{'user_id': uid} for uid in match_maked_users]
        )
        await self.trigger_bot_command(
            BotCommands.SEND_USER_WILL_NOT_TAKE_PART_IN_EVENT,
            [{'user_id': uid} for uid in not_match_maked_users]
        )
        LOGGER.debug(
            f'Notified users that registration is complete: '
            f'{len(match_maked_users)} will take part, '
            f'{len(not_match_maked_users)} will not'
        )
