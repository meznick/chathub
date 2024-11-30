import os
from datetime import datetime

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import Message, FSInputFile
from aiogram.utils.i18n import gettext as _
from aiogram.utils.media_group import MediaGroupBuilder

from bot import setup_logger
from bot.scenes.base import BaseSpeedDatingScene

LOGGER = setup_logger(__name__)


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
        """
        This method is triggered when the user enters the registration scene.

        If the user does not exist, it starts the registration process by calling
        the `_start_registration` method. If the user already exists, it sends
        a message to the user indicating that they can edit their profile.

        Note: This method requires a connection to a PostgreSQL database, which
        is obtained from the `get_connectors` method of a parent class.

        :param message: The message object received from the user.
        :param state: The FSMContext object for storing and retrieving conversation state.
        :param kwargs: Additional keyword arguments.
        """
        data = await state.get_data()
        step_name = data.get('step', '')
        LOGGER.debug(
            f'User entered registration Scene: '
            f'{message.from_user.id}[{step_name}]: {message.text}'
        )

        pg, *__ = self.get_connectors_from_context(kwargs)

        user = await pg.get_user(message.from_user.id)
        if not user:
            # if a user doesn't exist -- starting a registration process
            await self._start_registration(message, pg, state, step_name)
        else:
            # if a user exists - telling him that he can edit his profile
            await message.answer(
                _('user already exists'),
                parse_mode=ParseMode.HTML,
            )
            await self.wizard.exit()

    @on.message(F.text)
    async def on_message(self, message: Message, state: FSMContext, **kwargs):
        """
        This method processes all registration steps except for a photo step.

        :param message: The message object received.
        :param state: The FSMContext object representing the current state of the conversation.
        :param kwargs: Additional keyword arguments that may be passed to the method.
        """
        data = await state.get_data()
        step_name = data.get('step', '')
        LOGGER.debug(
            f'Got a message in registration Scene: '
            f'{message.from_user.id}[{step_name}]: {message.text}'
        )

        pg, *__ = self.get_connectors_from_context(kwargs)

        # processing registration steps
        if step_name == 'name':
            await self._update_user_name(message, pg, state)

        elif step_name == 'sex':
            await self._update_user_sex(message, pg, state)

        elif step_name == 'birthday':
            await self._update_user_birthday(message, pg, state)

        elif step_name == 'city':
            await self._update_user_city(message, pg, state)

    @on.message(F.photo)
    async def on_photo(self, message: Message, state: FSMContext, **kwargs):
        """
        This method processes a photo registration step.

        :param message: The message object received.
        :param state: The FSMContext object representing the current state of the conversation.
        :param kwargs: Additional keyword arguments that may be passed to the method.
        """
        data = await state.get_data()
        step_name = data.get('step', '')

        pg, __, s3, fm = self.get_connectors_from_context(kwargs)

        if step_name != 'photo':
            await message.answer(
                _(f'invite to send {step_name}'),
                parse_mode=ParseMode.HTML,
            )
        else:
            await self._update_user_photo(fm, message, pg, s3)
            await self.wizard.exit()

    @on.message()
    async def on_unknown_message(self, message: Message, state: FSMContext):
        """
        Handles the event when an unknown message is received while registering user.

        :param message: The unknown message received.
        :param state: The current state of the finite state machine.
        """
        ...

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext, **kwargs):
        """
        This method is triggered when the user exists the registration scene.
        On exiting (successful registration) user's profile is sent.

        :param message: The message object related to the event.
        :param state: The FSMContext object representing the state machine context.
        :param kwargs: Additional keyword arguments.
        :return: None

        """
        data = await state.get_data()
        step_name = data.get('step', '')
        LOGGER.debug(
            f'User left registration Scene: '
            f'{message.from_user.id}[{step_name}]'
        )
        pg, __, s3, fm = self.get_connectors_from_context(kwargs)

        if step_name != '':
            user, images = await self._get_user_profile_data(pg, message)
            await self._send_user_profile(fm, images, message, s3, user)

    @staticmethod
    async def _start_registration(message, pg, state, step_name):
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
            await pg.add_user(
                user_id=message.from_user.id,
                username=message.from_user.username
            )
        else:
            await message.answer(
                _(f'invite to send {step_name}'),
                parse_mode=ParseMode.HTML,
            )

    @staticmethod
    async def _update_user_name(message, pg, state):
        await pg.update_user(name=message.text, user_id=message.from_user.id)
        await message.answer(
            _('invite to enter sex'),
            parse_mode=ParseMode.HTML,
        )
        await state.update_data(step='sex')

    @staticmethod
    async def _update_user_sex(message, pg, state):
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

        await pg.update_user(sex=sex, user_id=message.from_user.id)
        await message.answer(
            _('invite to enter birthday'),
        )
        await state.update_data(step='birthday')

    @staticmethod
    async def _update_user_city(message, pg, state):
        await pg.update_user(city=message.text, user_id=message.from_user.id)
        await message.answer(
            _('invite to send photo'),
            parse_mode=ParseMode.HTML,
        )
        await state.update_data(step='photo')

    @staticmethod
    async def _update_user_birthday(message, pg, state):
        try:
            input_value = message.text
            birthday = datetime.strptime(input_value, '%Y-%m-%d').date()
            await pg.update_user(birthday=birthday, user_id=message.from_user.id)
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

    @staticmethod
    async def _update_user_photo(fm, message, pg, s3):
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

    @staticmethod
    async def _get_user_profile_data(pg, message):
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
            return
        # for now, showing only the latest image
        images = [await pg.get_latest_image_by_owner(message.from_user.id)]

        return user, images

    @staticmethod
    async def _send_user_profile(fm, images, message, s3, user):
        birth_date = user['birthday']
        today = datetime.now().date()
        media_group = MediaGroupBuilder(
            caption=_('your profile {name} {sex} {age} {city}').format(
                name=user['name'],
                sex=_('sex_male') if user['sex'].upper() == 'M' else _('sex_female'),
                age=(
                        today.year - birth_date.year - (
                            (today.month, today.day) < (birth_date.month, birth_date.day)
                        )
                ),
                city=user['city'],
            ),
        )

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


class ProfileEditingScene(RegistrationScene, state='profile_editing'):
    """
    Scene for profile editing.
    Editing steps are all the same as in registration scene.
    Current step is stored in context: state['step'].
    """

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, **kwargs):
        """
        This method is triggered when the user enters the registration scene.

        If the user does not exist, it starts the registration process by calling
        the `_start_registration` method. If the user already exists, it sends
        a message to the user indicating that they can edit their profile.

        Note: This method requires a connection to a PostgreSQL database, which
        is obtained from the `get_connectors` method of a parent class.

        :param message: The message object received from the user.
        :param state: The FSMContext object for storing and retrieving conversation state.
        :param kwargs: Additional keyword arguments.
        """
        data = await state.get_data()
        step_name = data.get('step', '')
        LOGGER.debug(
            f'User entered profile editing Scene: '
            f'{message.from_user.id}[{step_name}]: {message.text}'
        )

        pg, *__ = self.get_connectors_from_context(kwargs)

        user = await pg.get_user(message.from_user.id)
        if user:
            # if a user doesn't exist -- starting a registration process
            await self._start_editing(message, state, step_name)
        else:
            # this should not be the case, because normal user should not
            # enter editing mode before registration
            LOGGER.error(
                'Profile Editing Scene: '
                f'{message.from_user.id} wants to edit profile, '
                f'but he is not registered'
            )
            await message.answer(
                _('user does not exist'),
                parse_mode=ParseMode.HTML,
            )
            await self.wizard.exit()

    @staticmethod
    async def _start_editing(message, state, step_name):
        if step_name == '':
            await message.answer(
                _('starting editing message {name}').format(name=message.from_user.full_name),
                parse_mode=ParseMode.HTML,
            )
            await message.answer(
                _('invite to enter name'),
                parse_mode=ParseMode.HTML,
            )
            await state.update_data(step='name')
        else:
            await message.answer(
                _(f'invite to send {step_name}'),
                parse_mode=ParseMode.HTML,
            )
