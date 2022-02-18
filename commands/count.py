from lib.command import Command
from utils.messages import MessagesStorage
import telebot.types as types
from config.bot import bot, MESSAGES


class CountCommand(Command):
    name = "count"
    description = "Sends a number of saved messages to learn on"
    aliases = ["счётчик", "счетчик"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

    async def exec(self, message: types.Message):
        storage = MessagesStorage(message.chat.id)
        samples = await storage.count()
        samples += len(MESSAGES.get(message.chat.id) or [])
        return await bot.send_message(
            message.chat.id, f"✨ Сохранено {samples} строк для обучения"
        )
