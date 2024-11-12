from collections.abc import Callable
from datetime import datetime
from typing import Dict, List, Optional

from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import setup_logger
from bot.scenes.callback_data import (
    DatingMenuActionsCallbackData,
    DatingEventCallbackData,
    DatingEventActions, DatingMenuActions
)

LOGGER = setup_logger(__name__)


def manage_waiting_list(func):
    # @wraps
    async def wrapper(self, *args, **kwargs):
        chat_id = kwargs['chat_id']
        message_id = kwargs['message_id']
        try:
            result = await func(self, *args, **kwargs)
            self.delete_from_waiting(chat_id, message_id)
        except Exception as e:
            LOGGER.error(f'Got error while processing awaited data: {e}')
            result = False
        finally:
            LOGGER.debug(f'Awaited command data for {chat_id}[msg {message_id}]: {result}')
            return result

    return wrapper


class DataHandler:
    """
    Class for handling data from message broker.
    """
    waiting: Dict[str, Callable] = {}

    def wait_for_data(self, chat_id, message_id, handler):
        self.waiting.update({
            f'{chat_id}_{message_id}': handler
        })

    def delete_from_waiting(self, chat_id, message_id):
        del self.waiting[f'{chat_id}_{message_id}']

    @manage_waiting_list
    async def process_list_events(
            self,
            bot,
            chat_id: str,
            message_id: str,
            data: Optional[List[Dict]] = None
    ) -> bool:
        _ = bot.i18n.gettext
        bot = bot._bot
        builder = InlineKeyboardBuilder()

        if data:
            # generate keyboard with events
            for event in data:
                event_id = [key for key in event.keys()][0]
                start_time = datetime.strptime(
                    event[event_id]['start_time'],
                    '%Y-%m-%d %H:%M:%S',
                ).strftime(
                    '%Y-%m-%d %H:%M'
                )
                builder.button(
                    text=f'{event_id}: {start_time}',
                    callback_data=DatingEventCallbackData(
                        action=DatingEventActions.REGISTER,
                        event_id=event_id,
                        user_id=chat_id,
                    ),
                )

            builder.button(
                text=_('back button'),
                callback_data=DatingMenuActionsCallbackData(
                    action=DatingMenuActions.GO_DATING_MAIN_MENU
                ),
            )

            builder.adjust(1)
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=builder.as_markup(),
            )

        else:
            builder.button(
                text=_('back button'),
                callback_data=DatingMenuActionsCallbackData(
                    action=DatingMenuActions.GO_DATING_MAIN_MENU
                ),
            )
            builder.adjust(1)
            # edit message: there are no events
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=_('there are no events'),
                reply_markup=builder.as_markup(),
            )

        return True

    @manage_waiting_list
    async def get_confirmation(
            self,
            bot,
            chat_id: str,
            message_id: str,
            data: Dict[str, str]
    ) -> bool:
        """
        Processing result of an operation that returns just a status:
        success or failure.
        """
        _ = bot.i18n.gettext
        bot = bot._bot
        command_name = [key for key in data.keys()][0]
        succeed = data[command_name]
        if succeed:
            await bot.send_message(
                chat_id=chat_id,
                text=_('operation was succeeded'),
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=_('operation failed'),
                parse_mode=ParseMode.HTML,
            )
        return True
