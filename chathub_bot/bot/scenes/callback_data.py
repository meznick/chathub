from datetime import datetime

from aiogram.filters.callback_data import CallbackData


class DatingMenuActionsCallbackData(CallbackData, sep=':', prefix='dating_main_menu'):
    action: str
    value: str


class DatingEventCallbackData(CallbackData, sep=':', prefix='dating_event'):
    action: str
    event_id: int
    user_id: int
    event_time: datetime = None
