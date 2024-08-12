from aiogram import Router
from aiogram.filters import Command

from bot.scenes.registration import RegistrationScene

scenes_router = Router(name='scenes')

scenes_router.message.register(RegistrationScene.as_handler(), Command('start'))
