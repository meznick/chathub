from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from bot.scenes.dating import LOGGER


class CallbackI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        try:
            return event.from_user.language_code
        except AttributeError:
            LOGGER.error(f'No language code for action {event}!')
            return 'ru'


class StatisticsMiddleware(BaseMiddleware):
    """
    Middleware for collecting statistics for later publishing into prometheus.
    """
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        self.counter += 1
        data['counter'] = self.counter
        return await handler(event, data)


class LoggerMiddleware(BaseMiddleware):
    """
    Middleware for logging messages.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ):
        ...
