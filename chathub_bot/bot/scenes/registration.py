from datetime import datetime
from xml.sax import parse

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot import LOGGER
from bot.scenes.base import BaseSpeedDatingScene
from chathub_connectors.postgres_connector import AsyncPgConnector


class RegistrationScene(BaseSpeedDatingScene, state='registration'):
    """
    Scene for controlling registration process.
    Registration steps are:
    - providing name
    - providing sex
    - providing birthday
    - providing city
    - providing photo
    Current step is stored in context: state['step'].
    """

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, **kwargs):
        data = await state.get_data()
        step_name = data.get('step', '')
        LOGGER.debug(
            f'Registration Scene: '
            f'{message.from_user.id}[{step_name}]: {message.text}'
        )
        pg_connector = kwargs['bot'].pg
        LOGGER.debug(f'Trying to get user {message.from_user.id}...')
        user = await pg_connector.get_user(message.from_user.id)
        if not user:
            # if a user doesn't exist -- starting a registration process
            if step_name == '':
                await message.answer(
                    _('welcome message {name}').format(name=message.from_user.full_name),
                    parse_mode=ParseMode.HTML,
                )
                await message.answer(
                    _('invite to enter name'),
                    parse_mode=ParseMode.HTML,
                )
                await state.update_data(step='name')
                await pg_connector.add_user(
                    user_id=message.from_user.id,
                    username=message.from_user.username
                )
            else:
                LOGGER.warn(
                    f'User {message.from_user.id} entered '
                    f'RegistrationScene in state {step_name}'
                )
        else:
            # if a user exists - telling him that he can edit his profile
            await message.answer(
                _('user already exists'),
                parse_mode=ParseMode.HTML,
            )

    @on.message(F.text)
    async def on_message(self, message: Message, state: FSMContext, **kwargs):
        data = await state.get_data()
        step_name = data.get('step', '')
        LOGGER.debug(
            f'Registration Scene: '
            f'{message.from_user.id}[{step_name}]: {message.text}'
        )
        pg_connector = kwargs['bot'].pg

        if step_name == 'name':
            await pg_connector.update_user(name=message.text, user_id=message.from_user.id)
            await message.answer(
                _('invite to enter sex'),
                parse_mode=ParseMode.HTML,
            )
            await state.update_data(step='sex')

        elif step_name == 'sex':
            sex = message.text.upper()
            if sex not in ['M', 'F']:
                await message.answer(
                    _('wrong sex'),
                    parse_mode=ParseMode.HTML,
                )
            else:
                await pg_connector.update_user(sex=message.text, user_id=message.from_user.id)
                await message.answer(
                    _('invite to enter birthday'),
                )
                await state.update_data(step='birthday')

        elif step_name == 'birthday':
            try:
                input_value = message.text
                birthday = datetime.strptime(input_value, '%Y-%m-%d').date()
                await pg_connector.update_user(birthday=birthday, user_id=message.from_user.id)
                await message.answer(
                    _('invite to send city'),
                    parse_mode=ParseMode.HTML,
                )
                await state.update_data(step='city')
            except ValueError:
                await message.answer(
                    _('wrong date format'),
                    parse_mode=ParseMode.HTML,
                )

        elif step_name == 'city':
            await pg_connector.update_user(city=message.text, user_id=message.from_user.id)
            await message.answer(
                _('invite to send photo'),
                parse_mode=ParseMode.HTML,
            )
            await state.update_data(step='photo')

        elif step_name == 'photo':
            # photo is processed in on_photo method
            pass

    @on.message(F.photo)
    async def on_photo(self, message: Message, state: FSMContext):
        ...

    @on.message()
    async def on_unknown_message(self, message: Message, state: FSMContext):
        ...

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext):
        ...
