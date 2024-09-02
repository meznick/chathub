from aiogram import Router
from aiogram.filters import Command

from bot.scenes.dating import dating_router
from bot.scenes.profile import RegistrationScene, ProfileEditingScene

scenes_router = Router(name='scenes')

scenes_router.message.register(RegistrationScene.as_handler(), Command('start'))
scenes_router.message.register(ProfileEditingScene.as_handler(), Command('edit'))
scenes_router.include_router(dating_router)
