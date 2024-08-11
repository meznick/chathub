from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from . import LOGGER

test_router = Router(name='__name__')


@test_router.message(CommandStart())
async def handle_start(message: Message):
    LOGGER.debug(f'Got start command from {message.from_user.username}')
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}, welcome to the bot!")


@test_router.message()
async def echo(message: Message):
    LOGGER.debug(f'Got message from {message.from_user.username}')
    await message.send_copy(chat_id=message.chat.id)
