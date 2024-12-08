import json

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
        elif BotCommands.SEND_RULES.value in message:
            await self.send_pre_event_rules(user_id)
        elif BotCommands.INVITE_TO_MEETING.value in message:
            await self.send_meeting_invitation(message, headers)
        elif BotCommands.SEND_PARTNER_PROFILE.value in message:
            ...
        elif BotCommands.SEND_PARTNER_RATING_REQUEST.value in message:
            ...
        elif BotCommands.SEND_PARTNER_PROFILE_VERIFICATION_REQUEST.value in message:
            ...
        elif BotCommands.SEND_FINAL_DATING_MESSAGE.value in message:
            ...
        elif BotCommands.SEND_MATCH_MESSAGE.value in message:
            ...
        elif BotCommands.SEND_READY_FOR_EVENT_REQUEST.value in message:
            await self.send_ready_for_event_request(message, headers)
        elif BotCommands.SEND_BREAK_MESSAGE.value in message:
            ...
        else:
            raise UnknownBotCommandError(f'Cannot process command, message: {message[:100]}')
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

    async def send_pre_event_rules(self, user_id: int):
        _ = self.i18n.gettext

        await self.send_message(
            chat_id=user_id,
            text=_('event will start soon, heres rule remainder'),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        await self.send_message(
            chat_id=user_id,
            text=_('dating rules'),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    async def send_meeting_invitation(self, message: str, headers: dict):
        _ = self.i18n.gettext

        data = json.loads(message)[BotCommands.INVITE_TO_MEETING.value]

        await self.send_message(
            chat_id=headers.get('user_id'),
            text=_('meeting invitation {url}'.format(url=data.get('url'))),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    async def send_ready_for_event_request(self, message: str, headers: dict):
        _ = self.i18n.gettext

        builder = InlineKeyboardBuilder()
        builder.button(
            text=_('i am ready button'),
            callback_data=DatingEventCallbackData(
                action=DatingEventActions.READY.value,
                event_id=headers.get('event_id'),
                user_id=headers.get('user_id'),
                confirmed=False,
            ))

        await self.send_message(
            chat_id=headers.get('user_id'),
            text=_('are you ready to start event?'),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=builder.as_markup(),
        )
