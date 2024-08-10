from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession


class SpeedDatingBot:
    def __init__(self):
        self.session: AiohttpSession = AiohttpSession()
        self.bot: Bot = Bot(token="", session=self.session)
