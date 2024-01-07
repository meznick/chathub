from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.redis_connector import RedisConnector
from chathub_utils.auth import AuthProcessor
from fastapi import FastAPI, HTTPException

app = FastAPI()
redis_connector = RedisConnector(
    username='api_user',
    password='test',
)
postgres_connector = AsyncPgConnector(
    username='dev_service',
    password='devpassword'
)
auth_processor = AuthProcessor(
    redis_connector=redis_connector,
    postgres_connector=postgres_connector,
    secret=open("/dev/urandom", "rb").read(64).hex()
)


@app.get('/')
async def root():
    return {"status": 200, "data": "Hello World"}


@app.get('/login')
async def login(username: str, password: str):
    # validating credentials first to prevent injection attacks
    if not auth_processor.validate_credentials(username, password):
        raise HTTPException(status_code=401, detail="Invalid username or password 1")
    # try to authenticate user with creds
    auth_success = await auth_processor.authenticate(username, password)
    # generate JWT token
    if auth_success:
        return {'code': 200, 'token': auth_processor.generate_token(username)}
    else:
        raise HTTPException(status_code=403, detail="Invalid username or password 2")


@app.post('/register')
async def register(username: str, password1: str, password2: str, email: str):
    return {}


@app.get('/user/{username}')
async def user(username: str):
    return {}


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
