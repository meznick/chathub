import os
from datetime import datetime
from xml.sax import parse

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import Message, FSInputFile
from aiogram.utils.i18n import gettext as _
from aiogram.utils.media_group import MediaGroupBuilder

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
            if sex not in ['M', 'F', 'М', 'Ж']:
                await message.answer(
                    _('wrong sex'),
                    parse_mode=ParseMode.HTML,
                )
                return
            elif sex in ['М', 'Ж']:
                sex = 'M' if sex == 'М' else 'F'
            elif sex in ['M', 'F']:
                # let it be as is
                pass

            await pg_connector.update_user(sex=sex, user_id=message.from_user.id)
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

    @on.message(F.photo)
    async def on_photo(self, message: Message, state: FSMContext, **kwargs):
        data = await state.get_data()
        step_name = data.get('step', '')
        if step_name != 'photo':
            await message.answer(
                _(f'invite to send {step_name}'),
                parse_mode=ParseMode.HTML,
            )

        fm = kwargs['bot'].tfm
        s3 = kwargs['bot'].s3
        pg = kwargs['bot'].pg

        photo = message.photo[-1]
        # Can be useful for monitoring S3 cost
        # message.photo[-1].file_size
        photo_info = await message.bot.get_file(photo.file_id)
        file_extension = photo_info.file_path.split('.')[-1]
        tmp_file_path = fm.create_temp_file(
            suffix=file_extension
        )
        await message.bot.download(photo, tmp_file_path)
        s3_path = os.path.join(
            'user_photos',
            str(message.from_user.id),
            f'{int(datetime.now().timestamp())}.{file_extension}'
        )
        s3.upload_file(tmp_file_path, s3_path)
        fm.delete_temp_file(tmp_file_path)
        await pg.add_image(
            owner_id=message.from_user.id,  # if user exists verification?
            s3_bucket=s3.bucket_name,
            s3_path=s3_path,
        )
        await message.answer(
            _('registration complete'),
            parse_mode=ParseMode.HTML,
        )
        await self.wizard.exit()

    @on.message()
    async def on_unknown_message(self, message: Message, state: FSMContext):
        ...

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext, **kwargs):
        s3 = kwargs['bot'].s3
        pg = kwargs['bot'].pg
        fm = kwargs['bot'].tfm

        # get user data to represent
        user = await pg.get_user(message.from_user.id)
        if not user:
            LOGGER.error(
                f'Registration Scene: cannot find user {message.from_user.id} on exit'
            )
            await message.answer(
                _('internal error'),
                parse_mode=ParseMode.HTML,
            )
        images = await pg.get_images_by_owner(message.from_user.id)

        media_group = MediaGroupBuilder(
            caption=_('your profile {name} {sex} {age} {city}').format(
                name=user['name'],
                sex=_('sex_male') if user['sex'].upper() == 'M' else _('sex_female'),
                age=datetime.now().year - user['birthday'].year,  # is it correct?
                city=user['city'],
            ),
        )

        # build a message to send
        tmp_files = []
        for image in images:
            tmp_file_path = fm.create_temp_file(
                suffix=image['s3_path'].split('.')[-1]
            )
            tmp_files.append(tmp_file_path)
            s3.download_file(image['s3_path'], tmp_file_path)
            media_group.add(type='photo', media=FSInputFile(tmp_file_path))
        await message.bot.send_media_group(
            chat_id=message.chat.id,
            media=media_group.build()
        )

        # clear temp files
        for tmp_file in tmp_files:
            fm.delete_temp_file(tmp_file)
