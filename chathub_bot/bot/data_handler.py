from collections.abc import Callable
from functools import wraps
from typing import Dict, List, Optional

from aiogram.enums import ParseMode
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import setup_logger
from bot.scenes.dating import DatingMenuActionsCallbackData

LOGGER = setup_logger(__name__)


async def manage_waiting_list(func):
    data_handler = DataHandler()

    @wraps
    async def wrapper(*args, **kwargs):
        chat_id = kwargs['chat_id']
        message_id = kwargs['message_id']
        try:
            result = await func(*args, **kwargs)
            data_handler.delete_from_waiting(chat_id, message_id)
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
        if data:
            builder = InlineKeyboardBuilder()

            # generate keyboard with events
            builder.adjust(1)
            for event in data:
                event_id = [key for key in event.keys()][0]
                start_time = event[event_id]['start_time'].strftime('%Y-%m-%d %H:%M')
                builder.button(
                    text=f'{event_id}: {start_time}'
                )

            builder.button(
                text=_('back button'),
                callback_data=DatingMenuActionsCallbackData(
                    action='action',
                    value='go_dating_main_menu'
                ),
            )

            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=builder.as_markup(),
            )

        else:
            # edit message: there are no events
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=_('there are no events'),
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
