from fastapi import FastAPI
from pydantic import BaseModel

from src.api.auth import AuthProcessor

app = FastAPI()
auth_processor = AuthProcessor(
    # todo: change secret
    secret='test',
    redis_username='api_user',
)


@app.get('/')
async def root():
    return {"status": 200, "data": "Hello World"}


@app.get('/login')
async def login(username: str, password: str):
    # todo: return jwt token if creds are ok
    return {}


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
