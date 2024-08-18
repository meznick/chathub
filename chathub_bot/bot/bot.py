import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.memory import SimpleEventIsolation, MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from bot import (
    LOGGER, MESSAGE_BROKER_HOST, MESSAGE_BROKER_PORT,
    MESSAGE_BROKER_VIRTUAL_HOST, MESSAGE_BROKER_EXCHANGE, MESSAGE_BROKER_QUEUE,
    MESSAGE_BROKER_ROUTING_KEY, MESSAGE_BROKER_USERNAME, MESSAGE_BROKER_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
)
from bot.dev_router import dev_router
from bot.scenes import scenes_router, RegistrationScene
from bot.scenes.dating import DatingScene
from bot.scenes.profile_editing import ProfileEditingScene
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector


class DatingBot:
    def __init__(self, tg_token: str, debug: bool = False):
        self._bot = Bot(
            token=tg_token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
            )
        )

        self._pg = AsyncPgConnector(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            db=POSTGRES_DB,
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        self._rmq = RabbitMQConnector(
            host=MESSAGE_BROKER_HOST,
            port=MESSAGE_BROKER_PORT,
            virtual_host=MESSAGE_BROKER_VIRTUAL_HOST,
            exchange=MESSAGE_BROKER_EXCHANGE,
            queue=MESSAGE_BROKER_QUEUE,
            routing_key=MESSAGE_BROKER_ROUTING_KEY,
            username=MESSAGE_BROKER_USERNAME,
            password=MESSAGE_BROKER_PASSWORD,
            message_callback=self.process_rmq_message,
            caller_service='tg-bot',
            loglevel=logging.INFO,
        )

        self._dp = Dispatcher(
            # needed for fast user responses
            events_isolation=SimpleEventIsolation(),
            storage=MemoryStorage(),  # replace for Redis storage
            fsm_strategy=FSMStrategy.USER_IN_CHAT,  # choose a correct strategy
        )

        # include order makes sense!
        self._dp.include_router(scenes_router)
        self._dp.include_router(dev_router)

        self._dp.message.middleware(SimpleI18nMiddleware(
            i18n=I18n(
                path="bot/locales",
                default_locale="ru",
                domain="bot"
            ),
        ))

        sr = SceneRegistry(self._dp)
        sr.add(RegistrationScene)
        sr.add(ProfileEditingScene)
        sr.add(DatingScene)

        LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
        self._rmq.set_log_level(logging.DEBUG if debug else logging.INFO)

    def process_rmq_message(self, *args, **kwargs):
        # this method should be synchronous
        ...

    async def start_long_polling(self) -> None:
        LOGGER.debug('Starting long polling...')
        try:
            loop = asyncio.get_running_loop()
            self._rmq.run(custom_loop=loop)
            await self._dp.start_polling(self._bot)
        except KeyboardInterrupt:
            LOGGER.info('Shutting down...')
            self._rmq.disconnect()

    async def start_webhook(self) -> None:
        ...
