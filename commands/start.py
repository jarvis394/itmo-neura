from lib.command import Command
from config.replies import Reply
import telebot.types as types
from config.bot import bot


class StartCommand(Command):
    name = "start"
    description = "Starts your interaction with bot"
    aliases = []

    def __init__(self, *args) -> None:
        super().__init__(*args)

    async def exec(self, message: types.Message):
        await bot.send_chat_action(message.chat.id, "typing")
        await bot.send_message(message.chat.id, Reply.ON_START)
