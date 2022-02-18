from lib.command import Command
from config.replies import Reply
import telebot.types as types
from config.bot import bot


class HelpCommand(Command):
    name = "help"
    description = "Sends bot's commands"
    aliases = ["помощь"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

    async def exec(self, message: types.Message):
        await bot.send_message(message.chat.id, Reply.ON_HELP)
