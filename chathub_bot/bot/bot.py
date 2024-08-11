import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot import LOGGER
from bot.test_router import test_router

dp = Dispatcher()
dp.include_router(test_router)


def main(tg_token: str, long_polling: bool = True, debug: bool = False):
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
    LOGGER.debug('Preparing to run bot...')
    if long_polling:
        LOGGER.debug('Running in long polling mode...')
        asyncio.run(main_long_polling(tg_token))
    else:
        LOGGER.debug('Running in webhook mode...')
        asyncio.run(main_webhook(tg_token))


async def main_long_polling(token: str):
    bot = Bot(
        token=token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )
    LOGGER.debug('Staring long polling...')
    await dp.start_polling(bot)


async def main_webhook(token: str):
    ...
