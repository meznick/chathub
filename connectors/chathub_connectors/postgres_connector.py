import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import Optional, List

import asyncpg
from asyncpg import Record
from psycopg2.extras import RealDictRow

from chathub_connectors import setup_logger

LOGGER = setup_logger(__name__)
LOGGER.warning(f'Logger {LOGGER} is active')


class OptionalQueryParamIterator:
    def __init__(self, _max=10):
        self.current = 1
        self.max = _max

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.max:
            raise StopIteration
        return self.current


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
        self.pool: Optional[asyncpg.pool.Pool] = None
        self.loop: Optional[AbstractEventLoop] = None
        LOGGER.info('Async PG connector initialized')

    async def connect(self, custom_loop: asyncio.AbstractEventLoop = None):
        LOGGER.debug(f'Connecting to PG: {self._host}:{self._port}/{self._db}')
        if custom_loop:
            self.loop = custom_loop

        self.pool = await asyncpg.create_pool(
            min_size=5,
            max_size=10,
            host=self._host,
            port=self._port,
            database=self._db,
            user=self._username,
            password=self._password,
            timeout=10,
            loop=self.loop
        )
        LOGGER.info(f'PG connected to {self._host}:{self._port}/{self._db}')

    async def get_user(self, user_id: int) -> Optional[Record]:
        """
        :param user_id: ID of the user to fetch.
        :return: The user data fetched from the database.
        """
        request_query = 'SELECT * FROM users WHERE id = $1;'
        async with self.pool.acquire() as conn:
            data = await conn.fetchrow(request_query, user_id)
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
        async with self.pool.acquire() as conn:
            await conn.execute(
                request_query,
                user_id,
                username,
                password_hash,
                birthday,
                city,
                bio,
                sex,
                name,
                rating
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

        async with self.pool.acquire() as conn:
            await conn.execute(
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
        async with self.pool.acquire() as conn:
            await conn.execute(
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
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, owner_id)
        LOGGER.debug(f'Found {len(data)} images for owner {owner_id}')
        return data

    async def get_dating_events(
            self,
            user: Record = None,
            include_finished: bool = False,
            limit: int = 10,
            timezone='UTC',
            event_id: int = None,
            registration_available: bool = True,
    ) -> List[Record]:
        """
        List Dating Events

        Retrieve a list of dating events based on the provided parameters.

        :param registration_available: Show only events that user can register for.
        :param event_id: If specific event data needed, provide it here.
        :param timezone: Timezone to display time in.
        :param user: The user for whom the dating events are being listed.
        :param include_finished: A flag indicating if finished events should be
                    included in the result. Defaults to False.
        :param limit: The maximum number of events to retrieve. Defaults to 10.
        :return: A list of dating events.
        """
        param = OptionalQueryParamIterator()
        user_id = user.get("id") if user else None
        finished_filter = 'AND start_dttm > NOW()' if not include_finished else ''
        for_user = f'WHERE user_id = ${next(param)}' if user else ''
        specific_event_filter = f'AND e.id = ${next(param)}' if event_id else ''
        registration_available_filter = 'AND state_id < 2' if registration_available else ''
        limit = f'LIMIT {limit}'
        request_query = f"""
            SELECT DISTINCT 
                e.id,
                e.start_dttm at time zone '{timezone}' as start_dttm,
                s.state_name,
                CASE WHEN r.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS registered,
                users_limit
            FROM public.dating_events as e
            LEFT JOIN event_states as s ON e.state_id = s.id
            LEFT JOIN (
                SELECT *
                FROM public.dating_registrations
                {for_user}
            ) AS r ON e.id = r.event_id
            WHERE 1=1
                {finished_filter}
                {registration_available_filter}
                {specific_event_filter}
            ORDER BY start_dttm ASC
            {limit}
            ;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, *(
                param for param in (
                    user_id,
                    event_id
                ) if param is not None
            ))
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
            SELECT user_id, registered_on_dttm, confirmed_on_dttm, confirmation_event_sent
            FROM public.dating_registrations
            WHERE event_id = $1;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, event_id)
        LOGGER.debug(f'Found {len(data)} event registrations')
        return data

    async def save_event_confirmation_sent(
            self,
            event_id: int,
            user_ids: list
    ):
        request_query = """
            UPDATE public.dating_registrations
            SET confirmation_event_sent = TRUE
            WHERE user_id = ANY($1) AND event_id = $2;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(request_query, user_ids, event_id)
        LOGGER.debug(f'Event confirmation sending saved for event#{event_id} for users {user_ids}')

    async def get_event_participants(
            self,
            event_id: int,
    ) -> List[Record]:
        request_query = """
            WITH event_group_participants AS (
                SELECT event_id, group_no, (MAX(turn_no) + 1) * 2 AS participants
                FROM public.dating_event_groups
                WHERE event_id = $1
                GROUP BY event_id, group_no
            ),
            full_groups AS (
                SELECT group_no, event_id
                FROM dating_events as e
                JOIN event_group_participants AS p
                    ON e.id = p.event_id
                    AND e.users_limit = p.participants
            ),
            uids AS (
                SELECT user_1_id, user_2_id
                FROM full_groups AS g
                JOIN dating_event_groups AS ag 
                     ON ag.event_id = g.event_id 
                     AND ag.group_no = g.group_no
            )
            SELECT DISTINCT user_1_id as user_id
            FROM uids

            UNION ALL

            SELECT DISTINCT user_2_id as user_id
            FROM uids;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, event_id)
        LOGGER.debug(f'Found {len(data)} event participants')
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
        async with self.pool.acquire() as conn:
            await conn.execute(
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
        async with self.pool.acquire() as conn:
            await conn.execute(
                request_query, user.get('id'), event_id
            )
        LOGGER.debug(f'User {user.get("id")} confirmed registration for event {event_id}')

    async def set_event_state(self, event_id: int, state_id: int):
        request_query = """
            UPDATE public.dating_events
            SET state_id = $2
            WHERE id = $1;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                request_query, event_id, state_id
            )
        LOGGER.debug(f'Event state for event {event_id} set to {state_id}')

    async def put_event_data(self, data):
        request_query = """
            INSERT INTO public.dating_event_groups 
            (event_id, group_no, turn_no, user_1_id, user_2_id)
            VALUES ($1, $2, $3, $4, $5);
        """
        async with self.pool.acquire() as conn:
            await conn.executemany(request_query, data)
        LOGGER.debug(f'Inserted event groups')

    async def get_event_data(self, event_id: int):
        request_query = """
            WITH event_group_participants AS (
                SELECT event_id, group_no, (MAX(turn_no) + 1) * 2 AS participants
                FROM public.dating_event_groups
                WHERE event_id = $1
                GROUP BY event_id, group_no
            ),
            full_groups AS (
                SELECT group_no, event_id
                FROM dating_events as e
                JOIN event_group_participants AS p
                    ON e.id = p.event_id
                    AND e.users_limit = p.participants
            )
            SELECT deg.group_no, turn_no, user_1_id, user_2_id
            FROM public.dating_event_groups AS deg
            JOIN full_groups AS g
                 ON g.group_no = deg.group_no
                 AND g.event_id = deg.event_id;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, event_id)
        LOGGER.debug(f'Fetched event#{event_id} groups')
        return data

    async def set_user_ready_to_start(self, user_id: int, event_id: int):
        request_query = """
            UPDATE public.dating_registrations
            SET is_ready = TRUE
            WHERE user_id = $1 AND event_id = $2;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                request_query, user_id, event_id
            )
        LOGGER.debug(f'User {user_id} set to ready for event {event_id}')

    async def are_all_event_users_ready(self, event_id: int):
        request_query = """
            select sum(case when is_ready then 1 else 0 end)/count(*) = 1.0 as all_ready
            from dating_registrations
            where event_id = $1;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetchrow(request_query, event_id)
        LOGGER.debug(f'Are all event users ready for event#{event_id}: {data.get("all_ready")}')
        return data.get('all_ready')

    async def save_user_like(self, source_user_id: int, target_user_id: int, event_id: int):
        request_query = """
            INSERT INTO public.likes (source_user_id, target_user_id, event_id)
            VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(request_query, source_user_id, target_user_id, event_id)
        LOGGER.debug(f'User {source_user_id} likes user {target_user_id} in event {event_id}')

    async def save_user_dislike(self, source_user_id: int, target_user_id: int, event_id: int):
        request_query = """
            INSERT INTO public.dislikes (source_user_id, target_user_id, event_id)
            VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(request_query, source_user_id, target_user_id, event_id)
        LOGGER.debug(f'User {source_user_id} dislikes user {target_user_id} in event {event_id}')

    async def save_user_report(self, source_user_id: int, target_user_id: int, event_id: int):
        request_query = """
            INSERT INTO public.reports (source_user_id, target_user_id, event_id)
            VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(request_query, source_user_id, target_user_id, event_id)
        LOGGER.debug(f'User {source_user_id} reports user {target_user_id} in event {event_id}')

    async def get_user_matches(self, user_id: int, event_id: int):
        request_query = """
            SELECT user_1_id, user_2_id, username, name
            FROM public.matches
            INNER JOIN users ON users.id = matches.user_2_id
            WHERE user_1_id = $1 AND event_id = $2;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, user_id, event_id)
        LOGGER.debug(f'Fetched {len(data)} user matches for user {user_id} in event {event_id}')
        return data

    async def get_event_registrations_for_user(self, user: RealDictRow):
        request_query = """
            SELECT DISTINCT event_id
            FROM public.dating_registrations
            WHERE user_id = %s;
        """
        async with self.pool.acquire() as conn:
            data = await conn.fetch(request_query, user.get('id'))
        LOGGER.debug(f'Found {len(data)} event registrations for user {user.get("id")}')
        return data

    async def cancel_registration(self, user: Record, event_id: int):
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
        async with self.pool.acquire() as conn:
            await conn.fetch(cancel_query, user.get('id'), event_id)
        LOGGER.debug(f'User {user.get("id")} cancelled registration for event {event_id}')

    def __del__(self):
        loop = self.loop or asyncio.new_event_loop()
        if self.pool:
            try:
                close_task = loop.create_task(self.pool.terminate())
                asyncio.gather(close_task)
            except Exception as e:
                LOGGER.warning(f'Fail on closing connection: {e}')
            LOGGER.info(f'PG connection to {self._host}:{self._port}/{self._db} closed')
        LOGGER.debug('PG connector deleted')
