"""
Aiogram’s basics API is easy to use and powerful, allowing the implementation of
simple interactions such as triggering a command or message for a response.
However, certain tasks require a dialogue between the user and the bot. This is
where Scenes come into play.

More info:
https://docs.aiogram.dev/en/dev-3.x/dispatcher/finite_state_machine/scene.html
"""
import abc
from typing import Any, List

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene
from aiogram.types import Message


class BaseSpeedDatingScene(Scene, abc.ABC):
    @abc.abstractmethod
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        ...

    @abc.abstractmethod
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        ...

    @staticmethod
    def get_connectors(context: dict) -> List[object]:
        connectors_list = ['pg', 'rmq', 's3', 'tfm']
        return [getattr(context['bot'], connector) for connector in connectors_list]
