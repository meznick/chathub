import logging
from typing import Optional
from enum import Enum

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())

STATE_EXPIRATION_TIME_SECONDS = 60 * 60 * 2


class Action(Enum):
    START = 'start'
    STOP = 'stop'
    RECONNECT = 'reconnect'


class State(Enum):
    MAIN = 'main'
    CHAT = 'chat'
    MATCHMAKING = 'matchmaking'


class UserManager:
    def __init__(
            self,
            redis_connector,
            log_level: Optional[int] = logging.DEBUG
    ):
        self._redis_connector = redis_connector
        LOGGER.setLevel(log_level)
        LOGGER.info('User manager initialized')

    def set_user_state(self, username: str, state: State) -> None:
        self._redis_connector.client.setex(
            f'user:{username}:state',
            STATE_EXPIRATION_TIME_SECONDS,
            state
        )

    def get_user_state(self, username: str) -> str:
        return self._redis_connector.client.get(f'user:{username}:state')

    def start_chat(self, username: str) -> None:
        LOGGER.debug(f'{username} executed chat START (adding to MM)')
        # добавить пользователя в вейтлист матчмейкера (редис)
        # кинуть сигнал в брокер? кто-то должен подхватить этот сигнал и отправить юзеру сообщение что
        #   матчмейкинг пошел

    def stop_chat(self, username: str) -> None:
        LOGGER.debug(f'{username} executed chat STOP')
        # change user state
        # destroy match pair

    def reconnect_to_chat(self, username: str) -> None:
        LOGGER.debug(f'{username} executed chat RECONNECT')
        # ???
