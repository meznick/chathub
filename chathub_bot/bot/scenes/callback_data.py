from datetime import datetime
from enum import Enum

from aiogram.filters.callback_data import CallbackData


class DatingMenuActions(Enum):
    LIST_EVENTS = 'list_events'
    SHOW_RULES = 'show_rules'
    GO_DATING_MAIN_MENU = 'go_dating_main_menu'


class DatingMenuActionsCallbackData(CallbackData, sep=':', prefix='dating_main_menu'):
    action: DatingMenuActions


class DatingEventActions(Enum):
    REGISTER = 'register'
    CANCEL = 'cancel'
    CONFIRM = 'confirm'
    READY = 'ready'


class DatingEventCallbackData(CallbackData, sep=':', prefix='dating_event'):
    action: DatingEventActions
    event_id: int
    user_id: int
    confirmed: bool
