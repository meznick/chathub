import asyncio
from typing import Optional

import asyncpg


class AsyncPgConnector:
    def __init__(
            self,
            host: str,
            port: int,
            db: int,
            username: Optional[str] = None,
            password: Optional[str] = None,
    ):
        self._host = host
        self._port = port
        self._db = db
        self._username = username
        self._password = password
        self.client = None

    async def connect(self):
        self.client = await asyncpg.connect(
            host=self._host,
            port=self._port,
            database=self._db,
            user=self._username,
            password=self._password,
        )

    def __del__(self):
        asyncio.new_event_loop().run_until_complete(self.client.close())
