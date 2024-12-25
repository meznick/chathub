from typing import Any

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.utils import escape_markdown_v2 as __

from bot import setup_logger, DateMakerCommands, DATE_MAKER_ROUTING_KEY
from bot.scenes.base import BaseSpeedDatingScene
from bot.scenes.callback_data import (
    DatingMenuActionsCallbackData,
    DatingEventCallbackData,
    DatingEventActions, DatingMenuActions, PartnerActionsCallbackData, PartnerActions
)
from chathub_connectors.postgres_connector import AsyncPgConnector
from chathub_connectors.rabbitmq_connector import AIORabbitMQConnector

LOGGER = setup_logger(__name__)


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
    pg, rmq, s3, fm = DatingScene.get_connectors_from_query(query)

    if callback_data.action == DatingMenuActions.LIST_EVENTS:
        # triggered from the main menu
        await _handle_listing_events(query, rmq, query.bot)

    elif callback_data.action == DatingMenuActions.SHOW_RULES:
        # triggered from the main menu
        await _display_dating_rules(query)

    elif callback_data.action == DatingMenuActions.GO_DATING_MAIN_MENU:
        # triggered from anywhere
        await _display_main_menu(user_id=query.from_user.id, query=query, edit=True, pg=pg)


@dating_router.callback_query(DatingEventCallbackData.filter())
async def dating_event_callback_handler(
        query: CallbackQuery,
        callback_data: DatingEventCallbackData
):
    LOGGER.debug(f'Got callback from user {query.from_user.id}: {callback_data}')

    rmq: AIORabbitMQConnector
    pg, rmq, s3, fm = DatingScene.get_connectors_from_query(query)

    if callback_data.action == DatingEventActions.REGISTER:
        # triggered from the event list
        await _handle_event_registration(query, rmq, callback_data, query.bot)

    elif callback_data.action == DatingEventActions.CANCEL:
        # triggered from the main menu
        await _handle_cancelling_event_registration(query, rmq, callback_data, query.bot)

    elif callback_data.action == DatingEventActions.CONFIRM:
        # triggered from confirmation request message (commands handler)
        await _confirm_registration(query, callback_data, rmq, query.bot)

    elif callback_data.action == DatingEventActions.READY:
        await _user_ready_to_start_event(query, callback_data, pg, query.bot)


@dating_router.callback_query(PartnerActionsCallbackData.filter())
async def dating_partner_actions_callback_handler(
        query: CallbackQuery,
        callback_data: PartnerActionsCallbackData
):
    LOGGER.debug(f'Got callback from user {query.from_user.id}: {callback_data}')

    pg: AsyncPgConnector
    rmq: AIORabbitMQConnector
    pg, rmq, s3, fm = DatingScene.get_connectors_from_query(query)

    # triggered for partner rating request
    if callback_data.action == PartnerActions.LIKE:
        await _user_liked(query, callback_data, query.bot, pg)
    elif callback_data.action == PartnerActions.DISLIKE:
        await _user_disliked(query, callback_data, query.bot, pg)
    elif callback_data.action == PartnerActions.REPORT:
        await _user_reported(query, callback_data, query.bot, pg)


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
        text=_('dating rules button'),
        callback_data=DatingMenuActionsCallbackData(action=DatingMenuActions.SHOW_RULES),
    )
    builder.button(
        text=_('list events'),
        callback_data=DatingMenuActionsCallbackData(action=DatingMenuActions.LIST_EVENTS),
    )
    builder.button(
        text=_('cancel event registration'),
        callback_data=DatingEventCallbackData(
            action=DatingEventActions.CANCEL.value,
            event_id=0,
            user_id=user_id,
            confirmed=False,
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
            action=DatingMenuActions.GO_DATING_MAIN_MENU
        ),
    )

    await query.bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=__(_('dating rules')),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=builder.as_markup(),
    )


async def _handle_listing_events(
        query: CallbackQuery,
        rmq: AIORabbitMQConnector,
        bot,
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
    :param bot:
    :type bot: DataHandler
    :return:
    """
    LOGGER.debug(f'Listing events for user {query.from_user.id}')

    try:
        builder = InlineKeyboardBuilder()

        builder.button(
            text=_('back button'),
            callback_data=DatingMenuActionsCallbackData(
                action=DatingMenuActions.GO_DATING_MAIN_MENU
            ),
        )

        await query.bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=__(_('here is list of events')),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=builder.as_markup(),
        )
        await rmq.publish(
            message=DateMakerCommands.LIST_EVENTS.value,
            routing_key=DATE_MAKER_ROUTING_KEY,
            exchange='chathub_direct_main',
            headers={
                'user_id': str(query.from_user.id),
                'chat_id': str(query.message.chat.id),
                'message_id': str(query.message.message_id),
            },
        )
        bot.wait_for_data(query.message.chat.id, query.message.message_id, bot.process_list_events)

    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')


async def _handle_event_registration(
        query: CallbackQuery,
        rmq: AIORabbitMQConnector,
        callback_data: DatingEventCallbackData,
        bot,
):
    LOGGER.debug(f'Registering user {query.from_user.id} to event {callback_data.event_id}')
    try:
        builder = InlineKeyboardBuilder()

        builder.button(
            text=_('back button'),
            callback_data=DatingMenuActionsCallbackData(
                action=DatingMenuActions.GO_DATING_MAIN_MENU
            ),
        )

        dating_event = f'Event #{callback_data.event_id}'

        await query.bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=_('registering you to the event {event}').format(event=dating_event),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )
        await rmq.publish(
            message=DateMakerCommands.REGISTER_USER_TO_EVENT.value,
            routing_key=DATE_MAKER_ROUTING_KEY,
            exchange='chathub_direct_main',
            headers={
                'user_id': str(query.from_user.id),
                'chat_id': str(query.message.chat.id),
                'message_id': str(query.message.message_id),
                'event_id': str(callback_data.event_id),
            },
        )
        bot.wait_for_data(query.message.chat.id, query.message.message_id, bot.get_confirmation)

    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')


async def _handle_cancelling_event_registration(
        query: CallbackQuery,
        rmq: AIORabbitMQConnector,
        callback_data: DatingEventCallbackData,
        bot,
):
    LOGGER.debug(f'User {query.from_user.id} is cancelling registrations')

    try:
        if not callback_data.confirmed:
            await _ask_for_cancelling_confirmation(callback_data, query)
        else:
            await _cancel_registration(callback_data, bot, query, rmq)

    except TelegramBadRequest as e:
        LOGGER.warning(f'Got exception while processing callback: {e}')


async def _cancel_registration(callback_data, bot, query, rmq):
    await rmq.publish(
        message=DateMakerCommands.CANCEL_REGISTRATION.value,
        routing_key=DATE_MAKER_ROUTING_KEY,
        exchange='chathub_direct_main',
        headers={
            'user_id': str(query.from_user.id),
            'chat_id': str(query.message.chat.id),
            'message_id': str(query.message.message_id),
            'event_id': str(callback_data.event_id),
        },
    )
    bot.wait_for_data(query.message.chat.id, query.message.message_id, bot.get_confirmation)


async def _ask_for_cancelling_confirmation(callback_data, query):
    if callback_data.event_id == 0:
        # user wants to cancel all registrations
        message_text = _('are you sure you want to cancel all registrations?')
    else:
        # user wants to cancel one registration
        dating_event = f'Event #{callback_data.event_id}'
        message_text = _('are you sure you want to cancel registration to event {event}').format(
            event=dating_event
        )
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_('back button'),
        callback_data=DatingMenuActionsCallbackData(
            action=DatingMenuActions.GO_DATING_MAIN_MENU
        ),
    )
    builder.button(
        text=_('cancel registration'),
        callback_data=DatingEventCallbackData(
            action=DatingEventActions.CANCEL.value,
            event_id=callback_data.event_id,
            user_id=query.from_user.id,
            confirmed=True,
        ),
    )
    await query.bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(),
    )


async def _confirm_registration(query, callback_data, rmq, bot):
    LOGGER.debug(f'Confirming user {query.from_user.id} to event {callback_data.event_id}')
    dating_event = f'Event #{callback_data.event_id}'

    await query.bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=_('thanks for confirming registration for {event}').format(event=dating_event),
        parse_mode=ParseMode.HTML,
    )
    await rmq.publish(
        message=DateMakerCommands.CONFIRM_USER_EVENT_REGISTRATION.value,
        routing_key=DATE_MAKER_ROUTING_KEY,
        exchange='chathub_direct_main',
        headers={
            'user_id': str(query.from_user.id),
            'chat_id': str(query.message.chat.id),
            'message_id': str(query.message.message_id),
            'event_id': str(callback_data.event_id),
        },
    )
    bot.wait_for_data(query.message.chat.id, query.message.message_id, bot.get_confirmation)


async def _user_ready_to_start_event(query, callback_data, pg, bot):
    LOGGER.debug(f'User {query.from_user.id} is ready to start event {callback_data.event_id}')

    await pg.set_user_ready_to_start(
        user_id=callback_data.user_id,
        event_id=callback_data.event_id,
    )

    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=_('confirmed'),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def _user_liked(query, callback_data, bot, pg):
    await pg.save_user_like(
        source_user_id=callback_data.user_id,
        target_user_id=callback_data.partner_id,
        event_id=callback_data.event_id,
    )
    message = _("please rate partners performance")
    reaction = _("liked")
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=__(f'{message}\n\n{reaction}'),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def _user_disliked(query, callback_data, bot, pg):
    await pg.save_user_dislike(
        source_user_id=callback_data.user_id,
        target_user_id=callback_data.partner_id,
        event_id=callback_data.event_id,
    )
    message = _("please rate partners performance")
    reaction = _("disliked")
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=__(f'{message}\n\n{reaction}'),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def _user_reported(query, callback_data, bot, pg):
    await pg.save_user_report(
        source_user_id=callback_data.user_id,
        target_user_id=callback_data.partner_id,
        event_id=callback_data.event_id,
    )
    message = _("please rate partners performance")
    reaction = _("reported")
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=__(f'{message}\n\n{reaction}'),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
