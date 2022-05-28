from telebot.async_telebot import CancelUpdate
from telebot import types
from commands.generate import GenerateCommand
from config.constants import BOT_MENTION_PREFIX
from lib.middleware import Middleware
from utils import is_command


class MentionMiddleware(Middleware):
    name = "MentionMiddleware"

    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        if message.text and message.text.startswith(BOT_MENTION_PREFIX) and not is_command(message):
            command = GenerateCommand()
            await command.exec(message, should_reply=True)
            return CancelUpdate()

    async def post_process(self, message, data, exception):
        pass
