import asyncio
from datetime import datetime
from typing import Optional, List

import asyncpg
import psycopg2
from asyncpg import Record
from psycopg2 import Error
from psycopg2.extras import RealDictCursor, RealDictRow

from chathub_connectors import setup_logger

LOGGER = setup_logger(__name__)
LOGGER.warning(f'Logger {__name__} is active, level: {LOGGER.getEffectiveLevel()}')


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
        self.client: asyncpg.connection.Connection | None = None
        LOGGER.info('Async PG connector initialized')

    async def connect(self, custom_loop: asyncio.AbstractEventLoop = None):
        LOGGER.debug(f'Connecting to PG: {self._host}:{self._port}/{self._db}')
        self.client = await asyncpg.connect(
            host=self._host,
            port=self._port,
            database=self._db,
            user=self._username,
            password=self._password,
            timeout=10,
            loop=custom_loop
        )
        LOGGER.info(f'PG connected to {self._host}:{self._port}/{self._db}')

    async def get_user(self, user_id: int) -> Optional[Record]:
        """
        :param user_id: ID of the user to fetch.
        :return: The user data fetched from the database.
        """
        LOGGER.debug('getting')
        if not self.client:
            await self.connect()

        request_query = 'SELECT * FROM users WHERE id = $1;'
        data = await self.client.fetchrow(request_query, user_id)
        LOGGER.debug(f'User found: {data}')
        return data

    async def add_user(
        self,
        user_id: int,
        username: str,
        password_hash: Optional[str] = None,
        birthday: Optional[datetime.date] = None,
        city: Optional[str] = None,
        bio: Optional[str] = None,
        sex: Optional[str] = None,
        name: Optional[str] = None,
        rating: Optional[float] = 0.0
    ):
        """
        Adds a new user to the database.

        :param user_id: The ID of the user.
        :param username: The username of the user.
        :param password_hash: The hashed password of the user. (Optional)
        :param birthday: The birthday of the user. (Optional)
        :param city: The city of the user. (Optional)
        :param bio: The bio of the user. (Optional)
        :param sex: The sex of the user. (Optional)
        :param name: The name of the user. (Optional)
        :param rating: The rating of the user. (Optional, default is 0.0)
        :return: None
        """
        request_query = '''
            INSERT INTO users
            (
                id,
                username,
                password_hash,
                birthday,
                city,
                bio,
                sex,
                name,
                rating
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
        '''
        await self.client.execute(
            request_query, user_id, username, password_hash, birthday, city, bio, sex, name, rating
        )
        LOGGER.debug(f'User created: {username} [{user_id}]')

    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
        birthday: Optional[datetime.date] = None,
        city: Optional[str] = None,
        bio: Optional[str] = None,
        sex: Optional[str] = None,
        name: Optional[str] = None,
        rating: Optional[float] = None
    ):
        """
        Updates a user's information in the database.

        :param user_id: The ID of the user to update.
        :param username: (optional) The new username.
        :param password_hash: (optional) The new password hash.
        :param birthday: (optional) The new birthday in the format `YYYY-MM-DD`.
        :param city: (optional) The new city.
        :param bio: (optional) The new bio.
        :param sex: (optional) The new sex.
        :param name: (optional) The new name.
        :param rating: (optional) The new rating.
        :return: None

        This method updates a user's information in the database based on the provided parameters.
        It constructs an SQL query to update the specified fields for the user with the given
        `user_id`. If no fields are provided for update, the method simply logs a debug
        message and returns without performing any database operation.

        The SQL query is executed using the PostgreSQL client, and the updated
        user information is logged.

        Example usage:
        ```
        await update_user(123, username="new_username", city="New York")
        ```
        """
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

        if birthday is not None:
            set_clauses.append(f"birthday = ${i}")
            values.append(birthday)

        if city is not None:
            set_clauses.append(f"city = ${i}")
            values.append(city)

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
        request_query = f'''
            UPDATE users
            SET {set_queries}
            WHERE id = $1;
        '''
        LOGGER.debug(f'update_user query: {request_query}, params: {values}')

        await self.client.execute(
            request_query, user_id, *values
        )
        LOGGER.debug(f'User altered in postgres: {username} [{user_id}]')

    async def add_image(
            self,
            owner_id: int,
            s3_bucket: str,
            s3_path: str,
    ):
        """
        This method is used to add an image to the database.

        :param owner_id: An integer representing the unique identifier for the owner of the image.
        :param s3_bucket: A string representing the name of the S3 bucket where the image is stored.
        :param s3_path: A string representing the path of the image within the S3 bucket.
        :return: None
        """
        request_query = '''
                INSERT INTO images
                (
                    owner,
                    s3_bucket,
                    s3_path,
                    upload_dttm
                )
                VALUES ($1, $2, $3, NOW());
            '''
        await self.client.execute(
            request_query, owner_id, s3_bucket, s3_path
        )
        LOGGER.debug(f'New image for {owner_id} was created')

    async def get_latest_image_by_owner(self, owner_id: int) -> Optional[Record]:
        images = await self.get_images_by_owner(owner_id)
        return images[0] if images else None

    async def get_images_by_owner(self, owner_id: int) -> Optional[list[Record]]:
        """
        :param owner_id: ID of the owner to fetch images for.
        :return: A list of images belonging to the specified owner.
        """
        request_query = 'SELECT * FROM images WHERE owner = $1 ORDER BY upload_dttm DESC;'
        data = await self.client.fetch(request_query, owner_id)
        LOGGER.debug(f'Found {len(data)} images for owner {owner_id}')
        return data

    async def get_dating_events(
            self,
            user: Record = None,
            include_finished: bool = False,
            limit: int = 10
    ) -> List[Record]:
        """
        List Dating Events

        Retrieve a list of dating events based on the provided parameters.

        :param user: The user for whom the dating events are being listed.
        :param include_finished: A flag indicating if finished events should be
                    included in the result. Defaults to False.
        :param limit: The maximum number of events to retrieve. Defaults to 10.
        :return: A list of dating events.
        """

        user_id = user.get("id") if user else None
        only_finished = 'AND start_dttm > NOW()' if not include_finished else ''
        for_user = 'WHERE r.user_id = $1' if user else ''
        limit = f'LIMIT {limit}'
        request_query = f"""
            SELECT DISTINCT 
                e.id, 
                e.start_dttm, 
                CASE WHEN r.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS registered
            FROM public.dating_events as e
            LEFT JOIN (
                SELECT *
                FROM public.dating_registrations
                {for_user}
            ) AS r ON e.id = r.event_id
            WHERE 1=1
                {only_finished}
            ORDER BY start_dttm ASC
            {limit}
            ;
        """
        data = await self.client.fetch(request_query, (user_id,))
        LOGGER.debug(f'Found {len(data)} dating events')
        return data

    async def get_event_registrations(
            self,
            event_id: int
    ) -> List[Record]:
        """
        List Event Registrations.
        :param event_id:
        :return:
        """
        request_query = """
            SELECT user_id, registered_on_dttm, confirmed_on_dttm
            FROM public.dating_registrations
            WHERE event_id = $1;
        """
        data = await self.client.execute(request_query, event_id)
        LOGGER.debug(f'Found {len(data)} event registrations')
        return data

    async def register_for_event(
            self,
            user: Record,
            event_id: int
    ):
        """
        Method for adding new member to event.
        Remember to check if user already registered!

        :param user:
        :param event_id:
        :return:
        """
        request_query = """
            INSERT INTO public.dating_registrations (user_id, event_id)
            VALUES ($1, $2);
        """
        await self.client.execute(
            request_query, user.get('id'), event_id
        )
        LOGGER.debug(f'User {user.get("id")} registered for event {event_id}')

    async def confirm_registration(self, user: Record, event_id: int):
        """
        Method for registration confirmation.

        :param user:
        :param event_id:
        :return:
        """
        request_query = """
            UPDATE public.dating_registrations
            SET confirmed_on_dttm = NOW()
            WHERE user_id = $1 AND event_id = $2;
        """
        await self.client.execute(
            request_query, user.get('id'), event_id
        )
        LOGGER.debug(f'User {user.get("id")} confirmed registration for event {event_id}')

    def __del__(self):
        loop = asyncio.new_event_loop()
        if self.client:
            # it looks like it cannot close properly
            try:
                loop.run_until_complete(self.client.close())
            except Exception as e:
                LOGGER.warning(f'Fail on closing connection: {e}')
            LOGGER.info(f'PG connection to {self._host}:{self._port}/{self._db} closed')

        LOGGER.debug('PG connector deleted')


class PostgresConnection:
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
        self.client: psycopg2.extensions.connection | None = None
        LOGGER.info('Synchronous PG connector initialized')

    def connect(self):
        try:
            self.client = psycopg2.connect(
                host=self._host,
                dbname=self._db,
                user=self._username,
                password=self._password,
                port=self._port,
            )
            LOGGER.info("Connection to PostgreSQL DB successful")
        except Error as e:
            LOGGER.error(f"Error: {e}")

    def get_user(self, user_id: int) -> Optional[RealDictRow]:
        """
        :param user_id: ID of the user to fetch.
        :return: The user data fetched from the database.
        """
        if not self.client:
            self.connect()

        request_query = 'SELECT * FROM users WHERE id = %s;'
        data = self._fetch_results(request_query, (user_id,))[0]
        LOGGER.debug(f'Fetched user: {data}')
        return data

    def get_dating_events(
            self,
            user: Record = None,
            include_finished: bool = False,
            limit: int = 10
    ) -> List[RealDictRow]:
        """
        List Dating Events

        Retrieve a list of dating events based on the provided parameters.

        :param user: The user for whom the dating events are being listed.
        :param include_finished: A flag indicating if finished events should be
                    included in the result. Defaults to False.
        :param limit: The maximum number of events to retrieve. Defaults to 10.
        :return: A list of dating events.
        """
        user_id = user.get("id") if user else None
        only_finished = 'AND start_dttm > NOW()' if not include_finished else ''
        for_user = f'WHERE r.user_id = %s' if user else ''
        limit = f'LIMIT {limit}'
        request_query = f"""
            SELECT DISTINCT
                e.id,
                e.start_dttm,
                CASE WHEN r.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS registered
            FROM public.dating_events as e
            LEFT JOIN (
                SELECT *
                FROM public.dating_registrations
                {for_user}
            ) AS r ON e.id = r.event_id
            WHERE 1=1
                {only_finished}
            ORDER BY start_dttm ASC
            {limit}
            ;
        """
        data = self._fetch_results(request_query, (user_id, ))
        LOGGER.debug(f'Found {len(data)} dating events')
        return data

    def get_event_registrations(
            self,
            event_id: int
    ) -> List[RealDictRow]:
        """
        List Event Registrations.
        :param event_id:
        :return:
        """
        request_query = """
            SELECT user_id, registered_on_dttm, confirmed_on_dttm
            FROM public.dating_registrations
            WHERE event_id = %s;
        """
        data = self._fetch_results(request_query, (event_id,))
        LOGGER.debug(f'Found {len(data)} event registrations for event {event_id}')
        return data

    def get_event_registrations_for_user(self, user: RealDictRow):
        request_query = """
            SELECT DISTINCT event_id
            FROM public.dating_registrations
            WHERE user_id = %s;
        """
        data = self._fetch_results(request_query, (user.get('id'),))
        LOGGER.debug(f'Found {len(data)} event registrations for user {user.get("id")}')
        return data

    def register_for_event(
            self,
            user: Record,
            event_id: int
    ):
        """
        Method for adding new member to event.
        Remember to check if user already registered!

        :param user:
        :param event_id:
        :return:
        """
        request_query = """
            INSERT INTO public.dating_registrations (user_id, event_id)
            VALUES (%s, %s);
        """
        self._execute_query(request_query, (user.get('id'), event_id))
        LOGGER.debug(f'User {user.get("id")} registered for event {event_id}')

    def confirm_registration(self, user: Record, event_id: int):
        """
        Method for registration confirmation.

        :param user:
        :param event_id:
        :return:
        """
        request_query = """
            UPDATE public.dating_registrations
            SET confirmed_on_dttm = NOW()
            WHERE user_id = %s AND event_id = %s;
        """
        self._execute_query(request_query, (user.get('id'), event_id))
        LOGGER.debug(
            f'User {user.get("id")} confirmed registration for event {event_id}'
        )

    def cancel_registration(self, user: Record, event_id: int):
        """
        Method for registration cancellation.

        :param user:
        :param event_id:
        :return:
        """
        cancel_query = """
            DELETE FROM public.dating_registrations
            WHERE user_id = %s AND event_id = %s;
        """
        self._execute_query(cancel_query, (user.get('id'), event_id))
        LOGGER.debug(f'User {user.get("id")} cancelled registration for event {event_id}')

    def _execute_query(self, request_query, params=None):
        if self.client is None:
            print("No connection to database.")
            return
        try:
            with self.client.cursor() as cursor:
                cursor.execute(request_query, params)
                self.client.commit()
                print("Query executed successfully")
        except Error as e:
            print(f"Error: {e}")

    def _fetch_results(self, request_query, params=None):
        if self.client is None:
            print("No connection to database.")
            return
        try:
            with self.client.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(request_query, params)
                results = cursor.fetchall()
                return results
        except Error as e:
            print(f"Error: {e}")
            return None

    def close(self):
        if self.client:
            self.client.close()
            print("Connection closed")
