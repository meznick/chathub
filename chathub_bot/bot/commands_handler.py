from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import BotCommands
from bot.scenes.callback_data import DatingEventCallbackData, DatingEventActions


class UnknownBotCommandError(Exception):
    pass


class BotCommandsHandlerMixin:
    async def process_commands(self, message, headers: dict, user_id: int):
        if BotCommands.CONFIRM_USER_EVENT_REGISTRATION.value in message:
            await self.request_event_registration_confirmation(headers, user_id)
        else:
            raise UnknownBotCommandError(f'Cannot process command, message: {message[:30]}')
        return True

    async def request_event_registration_confirmation(self, headers: dict, user_id: int):
        _ = self.i18n.gettext
        events = await self.pg.get_dating_events(user={'id': user_id})
        target_event = [e for e in events if e.get('id') == headers.get('event_id', 0)][0]

        builder = InlineKeyboardBuilder()
        builder.button(
            text=_('confirm button'),
            callback_data=DatingEventCallbackData(
                action=DatingEventActions.CONFIRM.value,
                event_id=headers.get('event_id', 0),
                user_id=user_id,
                confirmed=False,
            )
        )
        await self.send_message(
            chat_id=user_id,
            text=_(
                'please confirm event registration. event will start at {event_start_time}'
            ).format(
                event_start_time=target_event.get('start_dttm')
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(),
        )
