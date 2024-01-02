from typing import Optional

from src.redis import UsesRedisMixin


class AuthProcessor(UsesRedisMixin):
    def __init__(
            self,
            secret: str,
            algorithm: str = 'HS256',
            redis_host: str = 'localhost',
            redis_port: int = 6379,
            redis_db: int = 0,
            redis_username: Optional[str] = None,
            redis_password: Optional[str] = None,
    ):
        super().__init__(redis_host, redis_port, redis_db, redis_username, redis_password)
        # todo: if no secret provided generate it from system random?
        self.secret = secret
        self.algorithm = algorithm

    def validate_credentials(self, username: str, password: str) -> bool:
        ...

    def generate_token(self, username: str, password: str) -> str:
        ...

    def verify_token(self, token: str) -> bool:
        ...

    def update_token_expiration(self, token: str) -> bool:
        ...
