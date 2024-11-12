from datetime import datetime
from enum import Enum

from aiogram.filters.callback_data import CallbackData


class DatingMenuActionsCallbackData(CallbackData, sep=':', prefix='dating_main_menu'):
    action: str
    value: str


class DatingEventActions(Enum):
    REGISTER = 'register'
    CANCEL = 'cancel'


class DatingEventCallbackData(CallbackData, sep=':', prefix='dating_event'):
    action: str
    event_id: int
    user_id: int
    event_time: datetime = None
