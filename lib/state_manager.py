from dataclasses import dataclass
from typing import Dict, Union
from telebot import types


@dataclass
class MessageState:
    counter: int


@dataclass
class UserState:
    awaiting_action: str
    initial_message: types.Message
    command: str


class StateManager:
    states: Dict[int, Union[MessageState, UserState]]

    def __init__(self) -> None:
        self.states = {}

    def has(self, id):
        return bool(self.states.get(id))

    def get(self, id):
        return self.states.get(id)

    def set(self, id, data):
        self.states[id] = data
        return True
    
    def remove(self, id):
        del self.states[id]
        return True
