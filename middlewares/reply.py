from telebot.async_telebot import CancelUpdate
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot import types
from commands.generate import GenerateCommand
from config.constants import BOT_ID


class ReplyMiddleware(BaseMiddleware):
    name = "ReplyMiddleware"

    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        if message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID:
            command = GenerateCommand()
            await command.exec(message)
            return CancelUpdate()

    async def post_process(self, message, data, exception):
        pass
