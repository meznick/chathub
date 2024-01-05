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
        ...

    def generate_token(self, username: str, password: str) -> str:
        ...

    def verify_token(self, token: str) -> bool:
        ...

    def update_token_expiration(self, token: str) -> bool:
        ...
