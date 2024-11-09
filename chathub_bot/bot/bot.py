import asyncio
import json
import logging

import aio_pika
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.memory import SimpleEventIsolation, MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from bot import (
    MESSAGE_BROKER_HOST, MESSAGE_BROKER_PORT,
    MESSAGE_BROKER_VIRTUAL_HOST, MESSAGE_BROKER_EXCHANGE, MESSAGE_BROKER_QUEUE,
    MESSAGE_BROKER_USERNAME, MESSAGE_BROKER_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
    AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_BUCKET, setup_logger
)
from bot.data_handler import DataHandler
from bot.dev_router import dev_router
from bot.middlewares import CallbackI18nMiddleware
from bot.scenes import scenes_router, RegistrationScene, ProfileEditingScene
from bot.scenes.dating import DatingScene
from bot.tmp_files_manager import TempFileManager
from chathub_connectors.aws_connectors import S3Client
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector

LOGGER = setup_logger(__name__)


class CustomBot(Bot):
    # to be able to use these connectors while handling events
    pg = None
    rmq = None
    s3 = None
    tfm = None

    # class for processing data collected from message broker
    dh = None

    # stats
    sent_messages = 0
    received_messages = 0

    def __init__(
        self,
        token: str,
        default: DefaultBotProperties,
    ):
        super().__init__(
            token=token,
            default=default
        )


class DatingBot:
    def __init__(self, tg_token: str, debug: bool = False):
        self._bot = CustomBot(
            token=tg_token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
            )
        )

        self._bot.dh = DataHandler()

        self._bot.pg = AsyncPgConnector(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            db=POSTGRES_DB,
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        self._bot.rmq = AIORabbitMQConnector(
            host=MESSAGE_BROKER_HOST,
            port=MESSAGE_BROKER_PORT,
            virtual_host=MESSAGE_BROKER_VIRTUAL_HOST,
            exchange=MESSAGE_BROKER_EXCHANGE,
            username=MESSAGE_BROKER_USERNAME,
            password=MESSAGE_BROKER_PASSWORD,
            caller_service='tg-bot',
        )

        self._bot.s3 = S3Client(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            bucket_name=AWS_BUCKET
        )

        self._bot.tfm = TempFileManager()

        self._dp = Dispatcher(
            # needed for fast user responses
            events_isolation=SimpleEventIsolation(),
            storage=MemoryStorage(),  # replace for Redis storage
            fsm_strategy=FSMStrategy.USER_IN_CHAT,  # choose a correct strategy
        )

        self._register_middlewares()
        self._setup_routing()

        LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)

    def _setup_routing(self):
        # include order makes sense!
        self._dp.include_router(scenes_router)
        self._dp.include_router(dev_router)
        sr = SceneRegistry(self._dp)
        sr.add(RegistrationScene)
        sr.add(ProfileEditingScene)
        sr.add(DatingScene)

    def _register_middlewares(self):
        # applying order makes sense!
        self._dp.message.middleware(SimpleI18nMiddleware(
            i18n=I18n(
                path="bot/locales",
                default_locale="ru",
                domain="bot"
            ),
        ))
        self._dp.callback_query.middleware(CallbackI18nMiddleware(
            i18n=I18n(
                path="bot/locales",
                default_locale="ru",
                domain="bot"
            )
        ))

    async def process_rmq_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process():
            print(message.body, message.properties.headers)
            chat_id = message.properties.headers["chat_id"]
            message_id = message.properties.headers["message_id"]
            key = f'{chat_id}_{message_id}'
            if await self._bot.dh.waiting[key](
                bot=self._bot,
                chat_id=chat_id,
                message_id=message_id,
                data=json.loads(message.body)
            ):
                await message.ack()

    async def start_long_polling(self) -> None:
        LOGGER.debug('Starting long polling...')
        try:
            loop = asyncio.get_running_loop()
            await self._bot.pg.connect(custom_loop=loop)
            await self._bot.rmq.connect(custom_loop=loop)
            await self._bot.rmq.listen_queue(
                queue_name=MESSAGE_BROKER_QUEUE,
                callback=self.process_rmq_message
            )
            await self._dp.start_polling(self._bot)

        except KeyboardInterrupt:
            LOGGER.info('Shutting down...')
            self._bot.rmq.disconnect()

    async def start_webhook(self) -> None:
        ...
