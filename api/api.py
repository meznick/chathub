from typing import Annotated

from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY
from fastapi import FastAPI, HTTPException, Header, Cookie, Response

from api.data_types import NewUser, User
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector
from chathub_connectors.redis_connector import RedisConnector
from chathub_utils.auth import AuthProcessor, RegisterError
from chathub_utils.auth import LoginError
from chathub_utils.user import UserManager, Action, State

app = FastAPI()
redis_connector = RedisConnector(
    host='10.132.179.6',  # zeph srv
    port=6379,
    username='api_user',
    password='test',
)
postgres_connector = AsyncPgConnector(
    host='10.132.179.6',  # zeph srv
    port=5432,
    username='dev_service',
    password='devpassword'
)
rmq_connector = RabbitMQConnector(
    host='10.132.179.6',  # zeph srv
    port=5672,
    username='api_service',
    password='apipassword'
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
    rmq_connector.publish('test', 'matchmaker', 'direct_main_dev')
    return {"status": 200, "data": "Hello World"}


@app.get('/login')
async def login(login_user: User, response: Response):
    try:
        token = await auth_processor.login(login_user.username, login_user.password)
    except LoginError:
        raise HTTPException(status_code=403, detail='Invalid username or password')
    else:
        response.set_cookie(key='jwt', value=token, httponly=True)
        user_manager.set_user_state(login_user.username, State.MAIN)
        return {'code': 200}


@app.post('/register')
async def register(new_user: NewUser):
    try:
        await auth_processor.register(new_user.username, new_user.password1, new_user.password2)
    except RegisterError as e:
        raise HTTPException(status_code=400, detail=f'Registration failed: {e}')
    else:
        # or redirect?
        # RedirectResponse(url='/login')
        return {'code': 200}


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
