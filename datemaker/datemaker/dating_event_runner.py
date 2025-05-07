import asyncio
import json
import time
from asyncio import sleep, AbstractEventLoop
from datetime import datetime, timedelta

import pandas as pd
from google.api_core.exceptions import FailedPrecondition
from grpc.aio import AioRpcError
from tzlocal import get_localzone

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector
from datemaker import (
    setup_logger,
    EventStateIDs,
    BotCommands,
    DEBUG,
    TG_BOT_ROUTING_KEY,
    RABBITMQ_EXCHANGE,
)
from .finite_state_machine import FiniteStateMachine, State
from .intelligent_agent import IntelligentAgent
from .meet_api_controller import GoogleMeetApiController

LOGGER = setup_logger(__name__)


class DateRunner:
    """
    Class that encapsulates logic for running singe date event.
    """

    send_rules_offset = timedelta(minutes=5)  # await asyncio.sleep(300) below

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
        self.start_time = start_time
        self.meet_api = meet_api_controller
        self.postgres = postgres_controller
        self.rabbitmq = rabbitmq_controller
        self.running = True
        self.debug = debug
        # data created in RegistrationConfirmationRunner
        self.event_data: pd.DataFrame | None = None
        self.user_ids_in_event = list
        self.meeting_spaces = []
        self.state_start_time = None
        self.is_ready_to_start = False  # flag when state machine is ready to start rounds
        self.participants = None
        loop = custom_event_loop or asyncio.get_event_loop()
        self.intelligence_agent = IntelligentAgent(loop, postgres_controller, debug=self.debug)
        LOGGER.info(
            f'DateRunner for event#{event_id} initialized. Start time: {start_time}'
            f'Debug mode: {self.debug}'
        )

    async def run_event(self):
        """
        Method for running actual dating event.
        A finite state machine pattern is used here.
        See readme for more info:
        https://github.com/meznick/chathub/blob/71b1b58d6bb6ae37e5f6e500da782c7dc3c40c79/datemaker/readme.md#L85
        """
        LOGGER.info(f'Dating event#{self.event_id} has started')
        await self.set_event_state(EventStateIDs.RUNNING)
        await self.collect_participants()
        await self.trigger_bot_to_send_rules()
        await self.get_event_prepared_data()
        # sleep for 300 seconds
        # because rules should be sent 5 mins before the event starts
        await asyncio.sleep(300)
        await asyncio.gather(*[
            self.run_dating_fsm(group_id)
            for group_id in self.event_data.group_no.unique().tolist()
        ])
        LOGGER.info(f'Dating event#{self.event_id} has finished')

    async def set_event_state(self, state: EventStateIDs):
        await self.postgres.set_event_state(self.event_id, state.value)

    async def collect_participants(self):
        """
        Collecting all users registered for event.
        """
        LOGGER.debug(f'Collecting registrations for event#{self.event_id}')
        self.participants = await self.postgres.get_event_participants(self.event_id)

    async def trigger_bot_to_send_rules(self):
        for user in self.participants:
            await self.rabbitmq.publish(
                message=BotCommands.SEND_RULES.value,
                routing_key=TG_BOT_ROUTING_KEY,
                exchange=RABBITMQ_EXCHANGE,
                headers={
                    'user_id': user.get('user_id'),
                    'chat_id': user.get('user_id'),
                    'event_id': self.event_id,
                }
            )
        LOGGER.debug(f'Sent rules to {len(self.participants)} users')

    async def get_event_prepared_data(self):
        """
        Collecting prepared data: dating groups and pairs.
        """
        self.event_data = pd.DataFrame(
            await self.postgres.get_event_data(self.event_id),
            columns=['group_no', 'turn_no', 'user_1_id', 'user_2_id']
        )
        self.user_ids_in_event = {
            int(uid)
            for uid
            in self.event_data.user_1_id.values.tolist() + self.event_data.user_2_id.values.tolist()
        }

    async def run_dating_fsm(self, group_id: int):
        """
        Running FSM that handles dating process.
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
        # states for fsm
        initial_state = State('initial', action=self.run_initial_state)
        round_state = State('round', action=self.run_dating_round)
        break_state = State('break', action=self.run_dating_break)
        final_state = State('final', action=self.run_dating_final)

        # transitions
        initial_state.add_transition('start', round_state)
        round_state.add_transition('break', break_state)
        break_state.add_transition('finish', final_state)
        break_state.add_transition('next', round_state)

        # initialize, start timer
        fsm = FiniteStateMachine(initial_state, group_id)
        # run transition to 1st round after the timer ends or all users ready
        while not self.is_ready_to_start:
            await sleep(10)

        rounds = self.event_data.turn_no.max() + 1  # turns start from 0
        LOGGER.debug(f'There will be {rounds} rounds for event#{self.event_id} group#{group_id}')
        if rounds == 0:
            await self.set_event_state(EventStateIDs.SKIPPED)
        else:
            for round_num in range(rounds):
                await fsm.transition('start' if round_num == 0 else 'next', round_num=round_num)
                # after 5 min transition to pause
                round_start_time = time.time()
                while time.time() - round_start_time < 300:
                    await sleep(10)
                await fsm.transition('break', round_num=round_num)
                # after 1 min transition to the next round
                break_start_time = time.time()
                while time.time() - break_start_time < 60:
                    await sleep(10)

            await fsm.transition('finish')

    async def run_initial_state(self):
        """
        Executes the initial state of the state machine, performing necessary setup
        and updates the readiness state.

        This method logs the current state of the state machine, initializes spaces
        required for the event, and updates the readiness flag once the setup is complete.
        """
        LOGGER.info('State machine is in initial state')
        # self.state_start_time = time.time()
        await self.create_spaces_for_event()
        # ready = await self.check_all_users_are_ready(send_requests=True)
        # start_time = await self.get_event_start_time()
        # while not (ready or start_time < datetime.now()):
        #     await sleep(10)
        #     ready = await self.check_all_users_are_ready()
        self.is_ready_to_start = True

    async def run_dating_round(self, round_num: int):
        LOGGER.info(f'State machine is running dating round #{round_num}')
        round_pairs = self.event_data.loc[self.event_data.turn_no == round_num]
        for i, row in round_pairs.iterrows():
            assert round_pairs.shape[0] <= len(self.meeting_spaces)
            await self.invite_to_meet_room(row, i)
            await self.send_partner_profiles(row)

    async def run_dating_break(self, round_num: int):
        LOGGER.info('State machine is in dating break')
        await self.stop_active_spaces()
        round_pairs = self.event_data.loc[self.event_data.turn_no == round_num]

        for user_id in self.user_ids_in_event:
            await self.send_break_message(user_id)
        LOGGER.debug(f'Sent break message to {len(self.user_ids_in_event)} users')

        for _, row in round_pairs.iterrows():
            await self.ask_to_rate_partner(row)
            # implement later
            # await self.ask_to_verify_partner_profile(row)

    async def run_dating_final(self):
        LOGGER.info('State machine is finishing dating event')
        for uid in self.user_ids_in_event:
            await self.send_final_event_message(uid)
        LOGGER.debug(f'Sent final message to {len(self.user_ids_in_event)} users')

        for uid in self.user_ids_in_event:
            await self.send_matches_message(uid)

        self.running = False
        await self.set_event_state(EventStateIDs.FINISHED)

    async def save_event_results(self):
        """
        See readme for more info:
        https://github.com/meznick/chathub/blob/f4a0aaf447e2af5518d6c88b217d1d0f260f15e0/datemaker/readme.md#L70
        :return:
        """
        while self.running:
            await sleep(100)
        LOGGER.info(f'Saving event results for event#{self.event_id}')

    async def create_spaces_for_event(self):
        """
        Create N spaces where N is the pair count in every round
        """
        for i in range(self.event_data.shape[0]):
            self.meeting_spaces.append(await self.meet_api.create_public_space())

        LOGGER.debug(f'Created {len(self.meeting_spaces)} meeting spaces for event#{self.event_id}')

    async def stop_active_spaces(self):
        for space in self.meeting_spaces:
            try:
                await self.meet_api.end_active_call(space)
            except (AioRpcError, FailedPrecondition):
                LOGGER.warning('In some meetings were no participants...')

        LOGGER.debug(f'Stopped all active meetings for event#{self.event_id}')

    async def check_all_users_are_ready(self, send_requests: bool = False):
        """
        Check if all users are ready to start event.
        :param send_requests: If "true" then triggering bot service to send requests to users.
        :return: True if all users are ready, false otherwise.
        """
        if send_requests:
            for uid in self.user_ids_in_event:
                await self.trigger_bot_command(
                    command=BotCommands.SEND_READY_FOR_EVENT_REQUEST,
                    user_id=uid,
                )
            LOGGER.debug(f'Sent ready for event requests to {len(self.user_ids_in_event)} users')
        are_all_ready = await self.postgres.are_all_event_users_ready(self.event_id)
        LOGGER.debug(f'All users are ready from DB: {are_all_ready}, debug: {DEBUG}')
        return DEBUG or are_all_ready

    async def get_event_start_time(self):
        events = await self.postgres.get_dating_events(timezone=get_localzone())
        try:
            start_time = [e['start_dttm'] for e in events if e['id'] == self.event_id][0]
        except (IndexError, KeyError):
            start_time = datetime.now()
        LOGGER.debug(f'Found event#{self.event_id} start time: {start_time}')
        return start_time

    async def invite_to_meet_room(self, row: pd.Series, room_number: int):
        """
        Invite users to their new meet rooms
        :param row: DF row containing user_1_id and user_2_id and some additional data
        :param room_number:
        """
        await self.trigger_bot_command(
            command=BotCommands.INVITE_TO_MEETING,
            user_id=int(row.user_1_id),
            data={
                'url': self.meeting_spaces[room_number].meeting_uri
            },
        )
        await self.trigger_bot_command(
            command=BotCommands.INVITE_TO_MEETING,
            user_id=int(row.user_2_id),
            data={
                'url': self.meeting_spaces[room_number].meeting_uri
            },
        )

    async def send_partner_profiles(self, row: pd.Series):
        """
        Send dating round partner's profiles to each other.
        :param row: DF row containing user_1_id and user_2_id and some additional data
        :return:
        """
        await self.trigger_bot_command(
            command=BotCommands.SEND_PARTNER_PROFILE,
            user_id=0,
            data={
                'partners': [int(row.user_1_id), int(row.user_2_id)]
            },
        )

    async def ask_to_rate_partner(self, row: pd.Series):
        await self.trigger_bot_command(
            command=BotCommands.SEND_PARTNER_RATING_REQUEST,
            user_id=int(row.user_1_id),
            data={
                'partner_id': int(row.user_2_id)
            },
        )
        await self.trigger_bot_command(
            command=BotCommands.SEND_PARTNER_RATING_REQUEST,
            user_id=int(row.user_2_id),
            data={
                'partner_id': int(row.user_1_id)
            },
        )

    async def ask_to_verify_partner_profile(self, row: pd.Series):
        await self.trigger_bot_command(
            command=BotCommands.SEND_PARTNER_PROFILE_VERIFICATION_REQUEST,
            user_id=int(row.user_1_id),
            data={
                'partner_id': int(row.user_2_id)
            },
        )
        await self.trigger_bot_command(
            command=BotCommands.SEND_PARTNER_PROFILE_VERIFICATION_REQUEST,
            user_id=int(row.user_2_id),
            data={
                'partner_id': int(row.user_1_id)
            },
        )

    async def send_break_message(self, user_id: int):
        await self.trigger_bot_command(
            command=BotCommands.SEND_BREAK_MESSAGE,
            user_id=user_id,
        )

    async def send_final_event_message(self, user_id: int):
        await self.trigger_bot_command(
            command=BotCommands.SEND_FINAL_DATING_MESSAGE,
            user_id=user_id,
        )

    async def send_matches_message(self, user_id: int):
        await self.trigger_bot_command(
            command=BotCommands.SEND_MATCH_MESSAGE,
            user_id=user_id,
        )

    async def trigger_bot_command(self, command: BotCommands, user_id: int, data: dict = None):
        await self.rabbitmq.publish(
            message=json.dumps({command.value: data}),
            routing_key=TG_BOT_ROUTING_KEY,
            exchange=RABBITMQ_EXCHANGE,
            headers={
                'user_id': user_id,
                'chat_id': user_id,
                'event_id': self.event_id,
            }
        )
