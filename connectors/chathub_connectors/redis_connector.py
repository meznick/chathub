import logging
from typing import Optional

import redis

from chathub_connectors import setup_logger

LOGGER = setup_logger(__name__)
LOGGER.warning(f'Logger {LOGGER} is active')


class RedisConnector:
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0,
            username: Optional[str] = None,
            password: Optional[str] = None,
            log_level: Optional[int] = logging.DEBUG,
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            username=username,
            password=password,
            decode_responses=True,
        )
        LOGGER.setLevel(log_level)
        LOGGER.info('Redis connector initialized')

    def add_user_to_matchmaker_queue(self, username: str):
        index = len(self.client.keys('matchmaker:queue'))
        self.client.set(f'matchmaker:queue:{index}', username)
        LOGGER.debug(f'User {username} added to MM queue as {index}')

    def __del__(self):
        self.client.close()
