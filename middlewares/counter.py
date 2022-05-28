from commands.generate import GenerateCommand
from telebot import types
from lib.middleware import Middleware
from config.states import states
from lib.state_manager import MessageState


class CounterMiddleware(Middleware):
    name = "CounterMiddleware"

    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        chat_id = message.chat.id
        state = states.get(chat_id)

        if not state:
            state = MessageState(counter=0)

        state.counter += 1

        if state.counter % 25 == 0:
            state.counter = 0
            command = GenerateCommand()
            await command.exec(message, ignore_error=True)

        states.set(chat_id, state)

    async def post_process(self, message, data, exception):
        pass
