from telebot.async_telebot import CancelUpdate
from telebot.asyncio_handler_backends import BaseMiddleware
from commands.start import StartCommand
from config.replies import Reply
from config.bot import bot
from telebot import types
from utils import is_command


class ChatMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        start_command = message.content_type == "text" and is_command(
            message, command=StartCommand
        )

        if (
            message.chat.type
            not in [
                "group",
                "superchat",
            ]
            and not start_command
        ):
            await bot.send_message(message.chat.id, Reply.ON_NOT_IN_GROUP)
            return CancelUpdate()

    async def post_process(self, message, data, exception):
        pass
