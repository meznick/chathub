from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from . import setup_logger

LOGGER = setup_logger(__name__)

"""
Router contains commands only for development purposes. Need to make sure
that users don't have access to these.
"""
dev_router = Router(name='__name__')


@dev_router.message(Command('debug'))
async def handle_debug(message: Message):
    LOGGER.debug(f'Got debug request from {message.from_user.username}')

    bot = message.bot
    bot.received_messages += 1

    await message.answer(
        "Current bot state\n"
        f"received messages: {bot.received_messages}\n"
        f"sent messages: {bot.sent_messages}\n",
        parse_mode=ParseMode.HTML,
    )
    bot.sent_messages += 1


@dev_router.message()
async def handle_that_was_not_processed(message: Message):
    LOGGER.debug(
        f'Got message {message.from_user.id}: "{message.text}" '
        f'that was not processed by any handler'
    )
