import re
from typing import Optional


class AuthProcessor:
    def __init__(self, redis_connector, secret: str, algorithm: Optional[str] = 'HS256'):
        # todo: create some interface for redis_connector type annotation
        self._redis_connector = redis_connector
        self._secret = secret
        self._algorithm = algorithm

    def get_algo(self):
        return self._algorithm

    def validate_credentials(self, username: str, password: str) -> bool:
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
        return bool(re.fullmatch(r'[a-zA-Z0-9_]{4,20}', username))

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

    def generate_token(self, username: str, password: str) -> str:
        ...

    def verify_token(self, token: str) -> bool:
        ...

    def update_token_expiration(self, token: str) -> bool:
        ...
