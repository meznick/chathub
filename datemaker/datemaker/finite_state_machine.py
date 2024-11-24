import asyncio
from collections.abc import Callable


class State:
    """Represents a state in the FSM."""

    def __init__(self, name, transitions: dict = None, action: Callable = None):
        self.name = name
        self.transitions = transitions or {}
        self.action = action

    def add_transition(self, _input: str, state):
        self.transitions[_input] = state

    def get_next_state(self, _input: str):
        return self.transitions.get(_input)

    async def run(self, *args, **kwargs):
        if self.action:
            return await self.action(*args, **kwargs)


class FiniteStateMachine:
    """A finite state machine."""

    def __init__(self, initial_state: State, **params):
        self.current_state = initial_state
        loop = asyncio.get_running_loop()
        loop.create_task(self.current_state.run(**params))

    async def transition(self, _input: str, **params):
        next_state = self.current_state.get_next_state(_input)
        if next_state:
            self.current_state = next_state
            print(f"Transitioned to {self.current_state.name}")
            await self.current_state.run(**params)
        else:
            print(f"No transition for input {_input} in state {self.current_state.name}")
