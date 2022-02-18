from abc import abstractmethod
from typing import List
from telebot import types


class Command:
    name: str
    """Command name"""

    description: str
    """Command description"""

    aliases: List[str]
    """Command aliases"""

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def exec(self, message: types.Message):
        """
        Command execution body
        """
