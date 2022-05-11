from lib.command import Command
from lib.messages import MessagesStorage
import telebot.types as types
from config.bot import bot, MESSAGES
from config.replies import Reply


class CountCommand(Command):
    name = "count"
    description = "Sends a number of saved messages to learn on"
    aliases = ["счётчик", "счетчик"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

    async def exec(self, message: types.Message):
        await bot.send_chat_action(message.chat.id, "typing")

        storage = MessagesStorage(message.chat.id)
        samples = await storage.count()
        samples += len(MESSAGES.get(message.chat.id) or [])
        return await bot.send_message(
            message.chat.id, Reply.ON_COUNT_COMMAND_REPLY.format(samples)
        )
