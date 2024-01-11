from argon2 import PasswordHasher
from argon2.profiles import RFC_9106_LOW_MEMORY

from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.redis_connector import RedisConnector
from chathub_utils.auth import AuthProcessor
from fastapi import FastAPI, HTTPException, Header

from utils.chathub_utils.auth import LoginError

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


@app.get('/')
async def root():
    return {"status": 200, "data": "Hello World"}


@app.get('/login')
async def login(username: str, password: str):
    try:
        token = auth_processor.login(username, password)
    except LoginError:
        raise HTTPException(status_code=403, detail="Invalid username or password")
    else:
        return {'code': 200, 'token': token}


@app.post('/register')
async def register(username: str, password1: str, password2: str, email: str):
    return {}


@app.get('/user/{username}')
async def user(username: str, authorization: str = Header(None)):
    # todo: get token from header
    jwt = None
    if not auth_processor.validate_token(jwt, username):
        raise HTTPException(status_code=403, detail="Forbidden")

    return {'code': 200, 'user': {'HERE WILL': 'BE USER DATA'}}


@app.post('/chat')
async def chat(message: str):
    # todo: api start chat
    # todo: api force stop chat
    # взять токен пользователя
    # получить айди пользователя по токену из редиса
    # проверить что пользователь не в чате? (подумать как такое может быть и что с этим делать)
    # добавить пользователя в вейтлист матчмейкера (редис)
    # кинуть сигнал в брокер? кто-то должен подхватить этот сигнал и отправить юзеру сообщение что
    #   матчмейкинг пошел
    return {}
