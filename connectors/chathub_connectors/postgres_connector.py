import asyncio
from typing import Optional
import logging

import asyncpg
from asyncpg import Record

LOGGER = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)
LOGGER.setLevel(logging.DEBUG)


class AsyncPgConnector:
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 5432,
            db: int = 'chathub_dev',
            username: Optional[str] = None,
            password: Optional[str] = None,
    ):
        self._host = host
        self._port = port
        self._db = db
        self._username = username
        self._password = password
        self.client = None
        LOGGER.info('PG connector initialized')

    async def connect(self):
        self.client = await asyncpg.connect(
            host=self._host,
            port=self._port,
            database=self._db,
            user=self._username,
            password=self._password,
        )
        LOGGER.info(f'Connected to {self._host}:{self._port}:{self._db}')

    async def get_user(self, username: str) -> Optional[Record]:
        """
        :param username: The username of the user to fetch.
        :return: The user data fetched from the database.
        """
        if not self.client:
            await self.connect()

        query = 'SELECT * FROM users WHERE username = $1;'
        data = await self.client.fetchrow(query, username)
        LOGGER.debug(f'Fetched user: {data}')
        return data

    async def add_user(
        self,
        username: str,
        password_hash: str,
        avatar_link: Optional[str] = None,
        bio: Optional[str] = None,
        sex: Optional[str] = None,
        name: Optional[str] = None,
        rating: Optional[float] = 0.0
    ):
        query = '''
            INSERT INTO users
            (
                username,
                password_hash,
                avatar_link,
                bio,
                sex,
                name,
                rating
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7);
        '''
        LOGGER.debug(f'Creating user: {username}')
        # todo: check if None values are passed as NULLs
        await self.client.execute(
            query, username, password_hash, avatar_link, bio, sex, name, rating
        )

    async def update_user(
        self,
        username: str,
        password_hash: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        sex: Optional[str] = None,
        name: Optional[str] = None,
        rating: Optional[float] = None
    ):
        pass

    def __del__(self):
        if self.client:
            # looks like it cannot close properly
            asyncio.new_event_loop().run_until_complete(self.client.close())
            LOGGER.info(f'PG connection to {self._host}:{self._port}:{self._db} closed')

        LOGGER.debug('PG connector deleted')
