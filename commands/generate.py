from lib.messages import MessagesStorage
from lib.command import Command
import telebot.types as types
from utils import generator, format
from loguru import logger
from config.replies import Reply
from config.bot import bot, MESSAGES


class GenerateCommand(Command):
    name = "generate"
    description = "Generates a random message based on chat history"
    aliases = ["g", "gen", "г", "рандом"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

    async def exec(
        self,
        message: types.Message,
        should_reply: bool = False,
        ignore_error: bool = False,
    ):
        await bot.send_chat_action(message.chat.id, "typing")
        storage = MessagesStorage(message.chat.id)

        messages = await storage.get()
        messages.extend(
            MESSAGES.get(message.chat.id) or []
        )  # Extend storage samples with samples in memory

        try:
            sentence = generator.generate(samples=messages, attempts=50)
        except Exception as e:
            logger.error(f"Could not generate message (should be critical error): {e}")

        if sentence:
            sentence = format.censor_sentence(sentence)
            sentence = format.improve_sentence(sentence)
            if should_reply:
                await bot.reply_to(message, sentence)
            else:
                await bot.send_message(message.chat.id, sentence)
        else:  # Not enough samples to generate message
            await bot.clear
            if not ignore_error:
                logger.warning(
                    f"Generate command failed for chat {message.chat.id}: not enough messages"
                )
                await bot.send_message(message.chat.id, Reply.ON_MESSAGES_DB_TOO_SMALL)
