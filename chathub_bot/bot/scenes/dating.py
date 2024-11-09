from datetime import datetime
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

from bot import setup_logger, DATE_MAKER_COMMANDS
from bot.scenes.base import BaseSpeedDatingScene
from bot.scenes.data_handler import DataHandler
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector

LOGGER = setup_logger(__name__)


class DatingMenuActionsCallbackData(CallbackData, sep=':', prefix='dating_main_menu'):
    action: str
    value: str


class DatingEventCallbackData(CallbackData, sep=':', prefix='dating_event'):
    action: str
    event_id: int
    user_id: int
    event_time: datetime = None


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
        rmq: AIORabbitMQConnector

        pg, rmq, s3, fm = self.get_connectors_from_context(kwargs)

        user = await pg.get_user(message.from_user.id)

        # show an entry message with inline controls.
        # inline handler will process further actions
        try:
            await _display_main_menu(message=message, pg=pg, edit=False)

        except TelegramBadRequest as e:
            LOGGER.warning(f'Got exception while processing callback: {e}')

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        LOGGER.debug(f'User {message.from_user.id} left dating scene')


dating_router = Router(name='__name__')
dating_router.message.register(DatingScene.as_handler(), Command('date'))
dating_router.callback_query.middleware(CallbackAnswerMiddleware())


@dating_router.callback_query(DatingMenuActionsCallbackData.filter())
async def dating_main_menu_actions_callback_handler(
        query: CallbackQuery,
        callback_data: DatingMenuActionsCallbackData
):
    LOGGER.debug(f'Got callback from user {query.from_user.id}: {callback_data}')

    pg: AsyncPgConnector
    rmq: AIORabbitMQConnector
    pg, rmq, s3, fm, dh = DatingScene.get_connectors_from_query(query)

    if callback_data.value == 'list_events':
        # triggered from the main menu
        await _handle_listing_events(query, rmq, dh)

    elif callback_data.value == 'show_rules':
        # triggered from the main menu
        await _display_dating_rules(query)

    elif callback_data.value == 'go_dating_main_menu':
        # triggered from anywhere
        await _display_main_menu(user_id=query.from_user.id, query=query, edit=True, pg=pg)


@dating_router.callback_query(DatingEventCallbackData.filter())
async def dating_event_callback_handler(
        query: CallbackQuery,
        callback_data: DatingEventCallbackData
):
    LOGGER.debug(f'Got callback from user {query.from_user.id}: {callback_data}')

    rmq: AIORabbitMQConnector
    pg, rmq, s3, fm, dh = DatingScene.get_connectors_from_query(query)

    if callback_data.value == 'event_register':
        # triggered from the event list
        await _handle_event_registration(query, rmq, callback_data)

    elif callback_data.value == 'cancel_event_registration':
        # triggered from the main menu
        await _handle_cancelling_event_registration(query, rmq, callback_data)


async def _display_main_menu(
        pg: AsyncPgConnector,
        user_id: int = None,
        edit: bool = False,
        query: CallbackQuery = None,
        message: Message = None,
):
    if query:
        query_uid = query.from_user.id
    else:
        query_uid = None

    if message:
        message_uid = message.from_user.id
    else:
        message_uid = None

    user_id = user_id or query_uid or message_uid

    LOGGER.debug(f'Displaying main menu for user {user_id}')

    builder = InlineKeyboardBuilder()
    builder.button(
        text=_('dating rules'),
        callback_data=DatingMenuActionsCallbackData(action='action', value='show_rules'),
    )
    builder.button(
        text=_('list events'),
        callback_data=DatingMenuActionsCallbackData(action='action', value='list_events'),
    )
    builder.button(
        text=_('cancel event registration'),
        callback_data=DatingEventCallbackData(
            action='cancel',
            event_id=0,
            user_id=user_id,
        ),
    )
    builder.adjust(1)

    user = await pg.get_user(user_id)

    if not edit:
        await message.answer(
            _('welcome to dating platform {name}').format(
                name=user.get('name')
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )
    else:
        await query.bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=_('welcome to dating platform {name}').format(
                name=user.get('name')
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )


async def _display_dating_rules(query):
    LOGGER.debug(f'Displaying rules for user {query.from_user.id}')

    builder = InlineKeyboardBuilder()
    builder.button(
        text=_('back button'),
        callback_data=DatingMenuActionsCallbackData(
            action='action',
            value='go_dating_main_menu'
        ),
    )

    await query.bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=_('dating rules'),
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(),
    )


async def _handle_listing_events(
        query: CallbackQuery,
        rmq: AIORabbitMQConnector,
        dh: DataHandler
):
    """
    This method logic:
    - update message text to be suitable for showing a list of events
    - send request to date maker to get the list

    Then bot.bot.DatingBot.process_rmq_message:
    - wait for response
    - update message and reply markup for selecting event

    For the second method and date maker to be able to process the response,
    need to pass additional headers:
    - user_id - for checking user's event registrations
    - chat_id - for updating menu
    - message_id - for updating menu

    :param query:
    :param rmq:
    :return:
    """
    LOGGER.debug(f'Listing events for user {query.from_user.id}')

    try:
        builder = InlineKeyboardBuilder()

        builder.button(
            text=_('back button'),
            callback_data=DatingMenuActionsCallbackData(
                action='action',
                value='go_dating_main_menu'
            ),
        )

        await query.bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=_('here is list of events'),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )
        await rmq.publish(
            message=DATE_MAKER_COMMANDS['list_events'],
            routing_key='date_maker_dev',
            exchange='chathub_direct_main',
            headers={
                'user_id': str(query.from_user.id),
                'chat_id': str(query.message.chat.id),
                'message_id': str(query.message.message_id),
            },
        )
        dh.wait_for_data(query.message.chat.id, query.message.message_id, dh.process_list_events)

    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')


async def _handle_event_registration(
        query: CallbackQuery,
        rmq: AIORabbitMQConnector,
        callback_data: DatingEventCallbackData
):
    LOGGER.debug(f'Registering user {query.from_user.id} to event {callback_data.event_id}')
    try:
        builder = InlineKeyboardBuilder()

        builder.button(
            text=_('back button'),
            callback_data=DatingMenuActionsCallbackData(action='action', value='go_dating_main_menu'),
        )

        dating_event = f'Event #{callback_data.event_id}: {callback_data.event_time}'

        await query.bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=_('registering you to the event {event}').format(event=dating_event),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )
        await rmq.publish(
            message=DATE_MAKER_COMMANDS['register_user_to_event'],
            routing_key='date_maker_dev',
            exchange='chathub_direct_main',
            headers={
                'user_id': str(query.from_user.id),
                'chat_id': str(query.message.chat.id),
                'message_id': str(query.message.message_id),
            },
        )

    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')


async def _handle_cancelling_event_registration(
        query: CallbackQuery,
        rmq: AIORabbitMQConnector,
        callback_data: DatingEventCallbackData
):
    try:
        if callback_data.event_id == 0:
            LOGGER.debug(f'User {query.from_user.id} is cancelling registration')

            builder = InlineKeyboardBuilder()
            builder.button(
                text=_('back button'),
                callback_data=DatingMenuActionsCallbackData(action='action',
                                                            value='go_dating_main_menu'),
            )
            builder.button(
                text=_('cancel registration'),
                callback_data=DatingEventCallbackData(
                    action='cancel',
                    event_id=callback_data.event_id,
                    user_id=query.from_user.id,
                ),
            )

            dating_event = f'Event #{callback_data.event_id}: {callback_data.event_time}'

            await query.bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                text=_('are you sure you want to cancel registration to event {event}').format(
                    event=dating_event
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=builder.as_markup(),
            )
        else:
            LOGGER.debug(
                f'User {query.from_user.id} is cancelling '
                f'registration to event {callback_data.event_id}'
            )

            builder = InlineKeyboardBuilder()
            builder.button(
                text=_('back button'),
                callback_data=DatingMenuActionsCallbackData(
                    action='action',
                    value='go_dating_main_menu'
                ),
            )

            await query.bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                text=_('your registration will be cancelled'),
                parse_mode=ParseMode.HTML,
                reply_markup=builder.as_markup(),
            )

            await rmq.publish(
                message=DATE_MAKER_COMMANDS['register_user_to_event'],
                routing_key='date_maker_dev',
                exchange='chathub_direct_main',
                headers={
                    'user_id': str(query.from_user.id),
                    'chat_id': str(query.message.chat.id),
                    'message_id': str(query.message.message_id),
                },
            )

    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')
