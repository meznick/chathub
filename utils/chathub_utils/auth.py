import logging
import re
from datetime import datetime, timedelta
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)

DATETIME_DUMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
TOKEN_EXPIRATION_TIME_HOURS = 2
TOKEN_REFRESH_DELTA_MINS = 60


class AuthProcessor:
    def __init__(
            self,
            redis_connector,
            postgres_connector,
            secret: str,
            algorithm: Optional[str] = 'HS256'
    ):
        # todo: create some interface for redis_connector type annotation
        self._redis_connector = redis_connector
        self._postgres_connector = postgres_connector
        self._secret = secret
        self._algorithm = algorithm
        self._password_hasher = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
        LOGGER.info('Auth processor initialized')

    def get_algo(self):
        return self._algorithm

    def validate_credentials(self, username: str, password: str) -> bool:
        LOGGER.debug('Validating credentials')
        return (
            self.validate_username(username)
            and self.validate_password(password)
        )

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validates the given username. Regex matches any string of 4 to 20 characters
        that consists of lowercase letters (a-z), uppercase letters (A-Z),
        digits (0-9), and underscores (_).

        :param username: The username to be validated.
        :return: Returns True if the username is valid, False otherwise.
        """
        return bool(re.fullmatch(r'^[a-zA-Z0-9_]{4,20}$', username))

    @staticmethod
    def validate_password(password: str) -> bool:
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

    async def authenticate(self, username: str, password: str) -> bool:
        # get user from pg
        user = await self._postgres_connector.get_user(username)
        if not user:
            LOGGER.debug('User does not exist')
            return False
        # compare hash from db with provided password's hash
        saved_hash = user.get('password_hash')
        if not self._password_hasher.verify(saved_hash, password):
            LOGGER.debug('Password does not match saved hash')
            return False
        return True

    def generate_token(self, username: str) -> str:
        payload = {
            'username': username,
            'expire_time': (
                    datetime.utcnow() +
                    timedelta(hours=TOKEN_EXPIRATION_TIME_HOURS)
            ).strftime(DATETIME_DUMP_FORMAT)
        }
        # put to cache with 50m expiration
        return jwt.encode(payload, key=self._secret, algorithm=self._algorithm)

    def verify_token(self, token: str) -> Optional[str]:
        # get from cache - if exists then do not make full verification
        payload = jwt.decode(token, key=self._secret, algorithms=[self._algorithm])
        if not payload:
            return
        elif datetime.strptime(payload['expire_time'], DATETIME_DUMP_FORMAT) < datetime.utcnow():
            return
        elif (
            datetime.strptime(payload['expire_time'], DATETIME_DUMP_FORMAT)
            - datetime.utcnow() < timedelta(minutes=TOKEN_REFRESH_DELTA_MINS)
        ):
            return self.generate_token(payload['username'])
        else:
            return token

    def update_token_expiration(self, token: str) -> bool:
        ...
