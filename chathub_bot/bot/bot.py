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
    MESSAGE_BROKER_HOST, MESSAGE_BROKER_PORT,
    MESSAGE_BROKER_VIRTUAL_HOST, MESSAGE_BROKER_EXCHANGE, MESSAGE_BROKER_QUEUE,
    MESSAGE_BROKER_ROUTING_KEY, MESSAGE_BROKER_USERNAME, MESSAGE_BROKER_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
    AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_BUCKET, setup_logger
)
from bot.scenes import scenes_router, RegistrationScene
from bot.scenes.dating import DatingScene
from bot.scenes.profile_editing import ProfileEditingScene
from bot.tmp_files_manager import TempFileManager
from chathub_connectors.aws_connectors import S3Client
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector

LOGGER = setup_logger(__name__)


class CustomBot(Bot):
    # to be able to use these connectors while handling events
    pg = None
    rmq = None
    s3 = None
    tfm = None

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

        self._bot.pg = AsyncPgConnector(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            db=POSTGRES_DB,
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        self._bot.rmq = RabbitMQConnector(
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
        self._bot.rmq.set_log_level(logging.DEBUG if debug else logging.INFO)

    def _setup_routing(self):
        # include order makes sense!
        self._dp.include_router(scenes_router)
        # self._dp.include_router(dev_router)
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

    def process_rmq_message(self, *args, **kwargs):
        # this method should be synchronous
        ...

    async def start_long_polling(self) -> None:
        LOGGER.debug('Starting long polling...')
        try:
            loop = asyncio.get_running_loop()
            self._bot.rmq.run(custom_loop=loop)
            await self._bot.pg.connect()
            await self._dp.start_polling(self._bot)
        except KeyboardInterrupt:
            LOGGER.info('Shutting down...')
            self._bot.rmq.disconnect()

    async def start_webhook(self) -> None:
        ...
