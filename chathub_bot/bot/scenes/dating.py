from typing import Any

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from bot import setup_logger
from bot.scenes.base import BaseSpeedDatingScene
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import RabbitMQConnector

LOGGER = setup_logger(__name__)


class TestCallbackData(CallbackData, sep=':', prefix='test'):
    action: str
    value: str


class DatingScene(BaseSpeedDatingScene, state='dating'):
    """
    WIP
    Class that processes events during dating.
    Keep in mind that some interactions can be made via mini-app.
    """
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, **kwargs) -> Any:
        LOGGER.debug(f'User {message.from_user.id} started dating')

        pg: AsyncPgConnector
        rmq: RabbitMQConnector

        pg, rmq, s3, fm = self.get_connectors_from_context(kwargs)

        user = await pg.get_user(message.from_user.id)

        # show an entry message with inline controls.
        # inline handler will process further actions
        builder = InlineKeyboardBuilder()

        builder.button(
            text=_('dating rules'),
            callback_data=TestCallbackData(action='action', value='edit_profile'),
        )
        builder.button(
            text=_('list events'),
            callback_data=TestCallbackData(action='action', value='list_events'),
        )
        builder.button(
            text=_('cancel event registration'),
            callback_data=TestCallbackData(action='action', value='cancel_event_registration'),
        )
        await message.answer(
            _('dating main menu message {name}').format(
                name=user.get('name')
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        pass


dating_router = Router(name='__name__')
dating_router.message.register(DatingScene.as_handler(), Command('date'))
dating_router.callback_query.middleware(CallbackAnswerMiddleware())


@dating_router.callback_query(TestCallbackData.filter(F.action == 'set'))
async def test_set_callback_handler(query: CallbackQuery, callback_data: TestCallbackData) -> None:
    LOGGER.debug(f'Got callback from user {query.from_user.id}: {callback_data}')
    builder = InlineKeyboardBuilder()

    builder.button(
        text="translatable btn 1",
        callback_data=TestCallbackData(action='set', value='1'),
    )
    builder.button(
        text="translatable btn 2",
        callback_data=TestCallbackData(action='set', value='2'),
    )

    # if an edited text equals the previous one, you will get an error:
    # aiogram.exceptions.TelegramBadRequest: Telegram server says -
    # Bad Request: message is not modified: specified new message content
    # and reply markup are exactly the same as a current content and reply
    # markup of the message
    try:
        await query.bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=f'You selected {callback_data.value}',
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')


@dating_router.callback_query(TestCallbackData.filter(F.action == 'action'))
async def actions_callback_handler(query: CallbackQuery, callback_data: TestCallbackData) -> None:
    LOGGER.debug(f'Got callback from user {query.from_user.id}: {callback_data}')
    pg, rmq, s3, fm = DatingScene.get_connectors_from_query(query)
    if callback_data.value == 'list_events':
        # send message to datemaker
        pass

    elif callback_data.value == 'event_register':
        # send message to datemaker
        pass

    elif callback_data.value == 'cancel_event_registration':
        # send message to datemaker
        pass
