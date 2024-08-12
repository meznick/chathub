from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from . import LOGGER

"""
Router contains commands only for development purposes. Need to make sure
that users don't have access to these.
"""
dev_router = Router(name='__name__')


@dev_router.message(CommandStart())
async def handle_start(message: Message):
    LOGGER.debug(f'Got start command from {message.from_user.username}')
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}, welcome to the bot!")


@dev_router.message()
async def echo(message: Message):
    LOGGER.debug(f'Got message from {message.from_user.username}')
    await message.send_copy(chat_id=message.chat.id)
