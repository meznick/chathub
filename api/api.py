from typing import Annotated

from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY
from fastapi import FastAPI, HTTPException, Header, Cookie, Response

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.redis_connector import RedisConnector
from chathub_utils.auth import AuthProcessor
from chathub_utils.auth import LoginError
from chathub_utils.user import UserManager, Action, State

app = FastAPI()
redis_connector = RedisConnector(
    username='api_user',
    password='test',
)
postgres_connector = AsyncPgConnector(
    username='dev_service',
    password='devpassword'
)
password_hasher = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
auth_processor = AuthProcessor(
    redis_connector=redis_connector,
    postgres_connector=postgres_connector,
    password_hasher=password_hasher,
    secret=open("/dev/urandom", "rb").read(64).hex(),
)
user_manager = UserManager(redis_connector=redis_connector)


@app.get('/')
async def root():
    return {"status": 200, "data": "Hello World"}


@app.get('/login')
async def login(username: str, password: str, response: Response):
    try:
        token = await auth_processor.login(username, password)
    except LoginError:
        raise HTTPException(status_code=403, detail='Invalid username or password')
    else:
        response.set_cookie(key='jwt', value=token, httponly=True)
        user_manager.set_user_state(username, State.MAIN)
        return {'code': 200}


@app.post('/register')
async def register(username: str, password1: str, password2: str, email: str):
    return {}


@app.get('/user/{username}')
async def user(username: str, jwt: str = Header(None)):
    # todo: get token from header
    jwt = None
    if not auth_processor.validate_token(jwt, username):
        raise HTTPException(status_code=403, detail='Forbidden')

    return {'code': 200, 'user': {'HERE WILL': 'BE USER DATA'}}


@app.post('/chat/{action}')
async def chat(action: Action, username: str, jwt: Annotated[str, Cookie()] = None):
    # валидировать токен
    token_valid = auth_processor.validate_token(jwt, username)
    if not token_valid:
        raise HTTPException(status_code=403, detail='Forbidden')
    user_state = user_manager.get_user_state(username)
    if action == 'start' and user_state == 'main':
        # starting new chat
        user_manager.start_chat(username)
    elif action == 'start' and user_state in ('chat', 'matchmaking'):
        # starting new chat after previous page close
        # maybe remove this branch?
        user_manager.start_chat(username)
    elif action == 'stop' and user_state in ('chat', 'matchmaking'):
        # stopping current chat\search
        user_manager.stop_chat(username)
    elif action == 'reconnect' and user_state == 'chat':
        # reconnecting to old chat
        user_manager.reconnect_to_chat(username)
    else:
        raise HTTPException(status_code=401, detail='Command does not match state')
    # if nothing was raised in user manager return success
    return {'code': 200, 'action': action}
