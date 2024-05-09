import abc
import logging
import re
from abc import ABCMeta
from datetime import datetime, timedelta
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError
from asyncpg import Record

LOGGER = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)

DATETIME_DUMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
TOKEN_EXPIRATION_TIME_SECONDS = 60 * 60 * 2
TOKEN_REFRESH_DELTA_SECONDS = 60 * 60


class LoginError(Exception):
    pass


class RegisterError(Exception):
    pass


class PostgresConnectorInterface(metaclass=ABCMeta):
    # todo: use interfaces for type annotations in AuthProcessor's init
    @abc.abstractmethod
    async def get_user(self, username: str) -> Optional[Record]:
        ...


class AuthProcessor:
    def __init__(
            self,
            redis_connector,
            postgres_connector,
            password_hasher: PasswordHasher,
            secret: str,
            algorithm: Optional[str] = 'HS256',
            log_level: Optional[int] = logging.DEBUG
    ):
        self._redis_connector = redis_connector
        self._postgres_connector = postgres_connector
        self._secret = secret
        self._algorithm = algorithm
        self._password_hasher = password_hasher
        LOGGER.setLevel(log_level)
        LOGGER.info('Auth processor initialized')
        LOGGER.debug(f'Secret: {self._secret}')

    def get_algo(self):
        return self._algorithm

    async def login(self, username: str, password: str):
        # validating credentials first to prevent injection attacks
        if not self._validate_credentials(username, password):
            raise LoginError('Invalid username or password 1')
        # try to authenticate user with creds
        auth_success = await self._authenticate(username, password)
        # generate JWT token
        if auth_success:
            # todo: this part can be skipped? =====
            cached_token = self._redis_connector.client.get(f'user:{username}:jwt')
            if cached_token:
                LOGGER.warning(
                    f'User {username} which is already logged in trying to login once more'
                )
            # until here ====================
            return self._generate_token(username)
        else:
            raise LoginError('Invalid username or password 2')

    async def register(self, username: str, password1: str, password2: str):
        if password1 != password2:
            raise RegisterError('Passwords do not match')
        if await self._is_user_exists(username):
            raise RegisterError('User already exists')

        self._postgres_connector.add_user(
            username=username,
            password_hash=self._password_hasher.hash(password1),
        )
        return True

    def validate_token(
            self,
            token: str,
            username: str,
            token_refresh_delta: Optional[int] = TOKEN_REFRESH_DELTA_SECONDS,
    ) -> Optional[str]:
        LOGGER.debug(f'Validating token: {token}')
        # get from cache - if exists then do not make full verification
        cached_token = self._redis_connector.client.get(f'user:{username}:jwt')
        if cached_token and (token != cached_token):
            # token is invalid
            return
        try:
            payload = jwt.decode(token, key=self._secret, algorithms=[self._algorithm])
        except jwt.exceptions.DecodeError:
            payload = None
        if not payload:
            # token cannot be decoded (basically invalid?)
            LOGGER.warning(f'Someone tried to login as {username} using invalid token')
            return
        if payload['username'] != username:
            # stolen token
            LOGGER.warning(
                f'{username} tried to login as {payload["username"]} using stolen token!'
            )
            return
        elif datetime.strptime(payload['expire_time'], DATETIME_DUMP_FORMAT) < datetime.utcnow():
            # token is expired
            LOGGER.debug('Token expired')
            return
        elif (
            datetime.strptime(payload['expire_time'], DATETIME_DUMP_FORMAT)
            - datetime.utcnow() < timedelta(seconds=token_refresh_delta)
        ):
            # token is fine but can be updated
            # drop previous key
            LOGGER.debug('Token nearly expired, generating new')
            return self._generate_token(payload['username'])
        else:
            # token is just fine
            LOGGER.debug('Token is fine')
            return token

    def _validate_credentials(self, username: str, password: str) -> bool:
        LOGGER.debug('Validating credentials')
        return (
            self._validate_username(username)
            and self._validate_password(password)
        )

    @staticmethod
    def _validate_username(username: str) -> bool:
        """
        Validates the given username. Regex matches any string of 4 to 20 characters
        that consists of lowercase letters (a-z), uppercase letters (A-Z),
        digits (0-9), and underscores (_).

        :param username: The username to be validated.
        :return: Returns True if the username is valid, False otherwise.
        """
        return bool(re.fullmatch(r'^[a-zA-Z0-9_]{4,20}$', username))

    @staticmethod
    def _validate_password(password: str) -> bool:
        """
        Validate the password using a regular expression pattern.
        At least 8 characters length
        Contains both uppercase and lowercase letters
        Contains at least one digit.
        Contains at least one special character (e.g. !@#$%^&*()).

        :param password: The password to be validated.
        :return: True if the password matches the pattern, False otherwise.
        """
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        return bool(re.fullmatch(pattern, password))

    async def _authenticate(self, username: str, password: str) -> bool:
        # get user from pg
        user = await self._is_user_exists(username)
        if not user:
            return False
        # compare hash from db with provided password's hash
        saved_hash = user.get('password_hash')
        try:
            self._password_hasher.verify(saved_hash, password)
        except InvalidHashError:
            LOGGER.debug('Password does not match saved hash')
            return False
        else:
            return True

    async def _is_user_exists(self, username: str) -> bool:
        user = await self._postgres_connector.get_user(username)
        if user:
            return user
        else:
            LOGGER.debug('User does not exist')
            return False

    def _generate_token(
            self,
            username: str,
            expiration_time: Optional[int] = TOKEN_EXPIRATION_TIME_SECONDS
    ) -> str:
        payload = {
            'username': username,
            'expire_time': (
                    datetime.utcnow() +
                    timedelta(seconds=expiration_time)
            ).strftime(DATETIME_DUMP_FORMAT)
        }
        token = jwt.encode(payload, key=self._secret, algorithm=self._algorithm)
        self._redis_connector.client.setex(
            f'user:{username}:jwt',
            TOKEN_EXPIRATION_TIME_SECONDS,
            token
        )
        return token
