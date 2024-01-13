import logging
from typing import Optional

import redis

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


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

    def __del__(self):
        self.client.close()
