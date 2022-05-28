from dataclasses import dataclass
from typing import Dict


@dataclass
class MessageState:
    counter: int


class StateManager:
    states: Dict[int, MessageState]

    def __init__(self) -> None:
        self.states = {}

    def has(self, id):
        return bool(self.states.get(id))

    def get(self, id):
        return self.states.get(id)

    def set(self, id, data):
        self.states[id] = data
        return True
