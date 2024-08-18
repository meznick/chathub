import asyncio
from typing import Optional

import asyncpg
from asyncpg import Record

from chathub_connectors import LOGGER


class AsyncPgConnector:
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 5432,
            db: str = 'chathub_dev',
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
        LOGGER.debug(f'Connecting to PG: {self._host}:{self._port}/{self._db}')
        self.client = await asyncpg.connect(
            host=self._host,
            port=self._port,
            database=self._db,
            user=self._username,
            password=self._password,
            timeout=10
        )
        LOGGER.info(f'PG connected to {self._host}:{self._port}/{self._db}')

    async def get_user(self, user_id: int) -> Optional[Record]:
        """
        :param user_id: ID of the user to fetch.
        :return: The user data fetched from the database.
        """
        if not self.client:
            await self.connect()

        query = 'SELECT * FROM users WHERE id = $1;'
        data = await self.client.fetchrow(query, user_id)
        LOGGER.debug(f'User found in postgres: {data}')
        return data

    async def add_user(
        self,
        user_id: int,
        username: str,
        password_hash: Optional[str] = None,
        bio: Optional[str] = None,
        sex: Optional[str] = None,
        name: Optional[str] = None,
        rating: Optional[float] = 0.0
    ):
        query = '''
            INSERT INTO users
            (
                id,
                username,
                password_hash,
                bio,
                sex,
                name,
                rating
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7);
        '''
        await self.client.execute(
            query, user_id, username, password_hash, bio, sex, name, rating
        )
        LOGGER.debug(f'User created in postgres: {username} [{user_id}]')

    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
        bio: Optional[str] = None,
        sex: Optional[str] = None,
        name: Optional[str] = None,
        rating: Optional[float] = None
    ):
        set_clauses = []
        i = 2
        values = []

        if username is not None:
            set_clauses.append(f"username = ${i}")
            i += 1
            values.append(username)

        if password_hash is not None:
            set_clauses.append(f"password_hash = ${i}")
            values.append(password_hash)

        if bio is not None:
            set_clauses.append(f"bio = ${i}")
            values.append(bio)

        if sex is not None:
            set_clauses.append(f"sex = ${i}")
            values.append(sex)

        if name is not None:
            set_clauses.append(f"name = ${i}")
            values.append(name)

        if rating is not None:
            set_clauses.append(f"rating = ${i}")
            values.append(rating)

        if not set_clauses:
            LOGGER.debug(f"No fields to update for user: {user_id}")
            return

        set_queries = ", ".join(set_clauses)
        query = f'''
            UPDATE users
            SET {set_queries}
            WHERE id = $1;
        '''
        LOGGER.debug(f'update_user query: {query}, params: {values}')

        await self.client.execute(
            query, user_id, *values
        )
        LOGGER.debug(f'User altered in postgres: {username} [{user_id}]')

    def __del__(self):
        if self.client:
            # it looks like it cannot close properly
            asyncio.new_event_loop().run_until_complete(self.client.close())
            LOGGER.info(f'PG connection to {self._host}:{self._port}/{self._db} closed')

        LOGGER.debug('PG connector deleted')
