from typing import Optional

import redis


class RedisConnector:
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0,
            username: Optional[str] = None,
            password: Optional[str] = None,
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            username=username,
            password=password,
            decode_responses=True,
        )

    def __del__(self):
        self.client.close()
