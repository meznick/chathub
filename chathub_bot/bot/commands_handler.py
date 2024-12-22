import json

from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import BotCommands
from bot.scenes.callback_data import DatingEventCallbackData, DatingEventActions, PartnerActions, \
    PartnerActionsCallbackData
from bot.utils import escape_markdown_v2 as __


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
            # implement later
            ...
        elif BotCommands.SEND_PARTNER_RATING_REQUEST.value in message:
            await self.send_partner_rating_request(message, headers)
        elif BotCommands.SEND_PARTNER_PROFILE_VERIFICATION_REQUEST.value in message:
            # implement later
            ...
        elif BotCommands.SEND_FINAL_DATING_MESSAGE.value in message:
            await self.send_final_dating_message(message, headers)
        elif BotCommands.SEND_MATCH_MESSAGE.value in message:
            await self.send_match_messages(message, headers)
        elif BotCommands.SEND_READY_FOR_EVENT_REQUEST.value in message:
            await self.send_ready_for_event_request(message, headers)
        elif BotCommands.SEND_BREAK_MESSAGE.value in message:
            await self.send_break_message(message, headers)
        else:
            raise UnknownBotCommandError(f'Cannot process command, message: {message[:100]}')
        return True

    async def request_event_registration_confirmation(self, headers: dict, user_id: int):
        _ = self.i18n.gettext
        events = await self.pg.get_dating_events(user={'id': int(user_id)})
        target_event = [e for e in events if e.get('id') == int(headers.get('event_id', 0))][0]

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
            text=__(_(
                'please confirm event registration. event will start at {event_start_time}'
            ).format(
                event_start_time=target_event.get('start_dttm')
            )),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=builder.as_markup(),
        )

    async def send_pre_event_rules(self, user_id: int):
        _ = self.i18n.gettext

        await self.send_message(
            chat_id=user_id,
            text=__(_('event will start soon, heres rule remainder')),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        await self.send_message(
            chat_id=user_id,
            text=__(_('dating rules')),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    async def send_meeting_invitation(self, message: str, headers: dict):
        _ = self.i18n.gettext

        data = json.loads(message)[BotCommands.INVITE_TO_MEETING.value]

        await self.send_message(
            chat_id=headers.get('user_id'),
            text=__(_('meeting invitation {url}'.format(url=data.get('url')))),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    async def send_partner_rating_request(self, message: str, headers: dict):
        _ = self.i18n.gettext

        data = json.loads(message)[BotCommands.SEND_PARTNER_RATING_REQUEST.value]
        partner_id = int(data.get('partner_id'))

        builder = InlineKeyboardBuilder()
        builder.button(
            text=_('like button'),
            callback_data=PartnerActionsCallbackData(
                action=PartnerActions.LIKE.value,
                event_id=headers.get('event_id'),
                user_id=headers.get('user_id'),
                partner_id=partner_id,
            )
        )
        builder.button(
            text=_('dislike button'),
            callback_data=PartnerActionsCallbackData(
                action=PartnerActions.DISLIKE.value,
                event_id=headers.get('event_id'),
                user_id=headers.get('user_id'),
                partner_id=partner_id,
            )
        )
        builder.button(
            text=_('report button'),
            callback_data=PartnerActionsCallbackData(
                action=PartnerActions.REPORT.value,
                event_id=headers.get('event_id'),
                user_id=headers.get('user_id'),
                partner_id=partner_id,
            )
        )

        await self.send_message(
            chat_id=headers.get('user_id'),
            text=__(_("please rate partners performance")),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=builder.as_markup(),
        )

    async def send_final_dating_message(self, message: str, headers: dict):
        _ = self.i18n.gettext

        await self.send_message(
            chat_id=headers.get('user_id'),
            text=__(_('final dating message')),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    async def send_match_messages(self, message: str, headers: dict):
        _ = self.i18n.gettext

        matches = await self.pg.get_user_matches(
            user_id=int(headers.get('user_id')),
            event_id=int(headers.get('event_id')),
        )

        for match in matches:
            await self.send_message(
                chat_id=headers.get('user_id'),
                text=__(_('you match with {partner_name}, his contact {partner_contact}').format(
                    partner_name=match.get('name'),
                    partner_contact=f'@{match.get("username")}',
                )),
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

    async def send_break_message(self, message: str, headers: dict):
        _ = self.i18n.gettext

        await self.send_message(
            chat_id=headers.get('user_id'),
            text=__(_('break message')),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
