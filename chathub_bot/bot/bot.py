import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.memory import SimpleEventIsolation, MemoryStorage

from bot import (
    LOGGER, MESSAGE_BROKER_HOST, MESSAGE_BROKER_PORT,
    MESSAGE_BROKER_VIRTUAL_HOST, MESSAGE_BROKER_EXCHANGE, MESSAGE_BROKER_QUEUE,
    MESSAGE_BROKER_ROUTING_KEY, MESSAGE_BROKER_USERNAME, MESSAGE_BROKER_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
)
from bot.dev_router import dev_router
from bot.message_broker_callback import process_message
from bot.scenes import scenes_router, RegistrationScene
from bot.scenes.dating import DatingScene
from bot.scenes.profile_editing import ProfileEditingScene
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector

dp = Dispatcher(
    # needed for fast user responses
    events_isolation=SimpleEventIsolation(),
    storage=MemoryStorage(),  # replace for Redis storage
)
dp.include_router(dev_router)
dp.include_router(scenes_router)
sr = SceneRegistry(dp)
sr.add(RegistrationScene)
sr.add(ProfileEditingScene)
sr.add(DatingScene)

rmq = RabbitMQConnector(
    host=MESSAGE_BROKER_HOST,
    port=MESSAGE_BROKER_PORT,
    virtual_host=MESSAGE_BROKER_VIRTUAL_HOST,
    exchange=MESSAGE_BROKER_EXCHANGE,
    queue=MESSAGE_BROKER_QUEUE,
    routing_key=MESSAGE_BROKER_ROUTING_KEY,
    username=MESSAGE_BROKER_USERNAME,
    password=MESSAGE_BROKER_PASSWORD,
    message_callback=process_message,
    caller_service='tg-bot',
    loglevel=logging.INFO,
)

pg = AsyncPgConnector(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    db=POSTGRES_DB,
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
)


def main(tg_token: str, long_polling: bool = True, debug: bool = False) -> None:
    """
    This method is the entry point for running the bot.
    It initializes the logging level based on the debug parameter.
    Depending on launch flags, bot is run in long polling or webhook mode.

    :param tg_token: The token for the Telegram bot.
    :param long_polling: A boolean indicating whether to run the bot in long
            polling mode or webhook mode.
            Defaults to True.
    :param debug: A boolean indicating whether to enable debug logging.
    Defaults to False.
    :return: None
    """
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
    rmq.set_log_level(logging.DEBUG if debug else logging.INFO)

    LOGGER.debug('Preparing to run bot...')
    if long_polling:
        LOGGER.debug('Running in long polling mode...')
        asyncio.run(start_long_polling(tg_token))
    else:
        LOGGER.debug('Running in webhook mode...')
        asyncio.run(start_webhook(tg_token))


async def start_long_polling(token: str) -> None:
    bot = Bot(
        token=token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )
    LOGGER.debug('Starting long polling...')
    try:
        loop = asyncio.get_running_loop()
        rmq.run(custom_loop=loop)
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        LOGGER.info('Shutting down...')
        rmq.disconnect()


async def start_webhook(token: str) -> None:
    ...
