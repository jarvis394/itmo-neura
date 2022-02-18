from typing import Dict, List
from config.constants import (
    BOT_MENTION_PREFIX,
    BOT_PREFIX,
    MESSAGES_SAMPLES_DIR,
    MESSAGES_FLUSH_INTERVAL,
)
from config.keys import TELEGRAM_BOT_API_TOKEN
from telebot.async_telebot import AsyncTeleBot, CancelUpdate
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot import types
from loguru import logger
from functools import partial
from config.commands import Command, set_bot_commands
from config.replies import Reply
import aioschedule
import asyncio
import telebot
import sys
from utils import generator, format
from utils.messages import MessagesStorage
import os


# This is used to store messages in memory and then
# flush them into storage when they overflow
MESSAGES: Dict[int, List[str]] = {}


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        logger.exception(exception)


class ChatMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        start_command = command_handler(message, command=Command.START)

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


def command_handler(message: types.Message, command: List[str]):
    """
    Custom message handler that activates on mention or slash commands

    Example:
    /start or @mention_prefix start or @mention_prefix, start
    """
    text = message.text.strip()
    args = text.split(" ")

    if len(args) > 1:
        return args[0].startswith(BOT_MENTION_PREFIX) and args[1] in command
    elif len(args) == 1:
        return args[0].startswith(BOT_PREFIX) and (
            text[len(BOT_PREFIX) :] in command
            or text[len(BOT_PREFIX) : -len(BOT_MENTION_PREFIX)] in command
        )
    else:
        return False


bot = AsyncTeleBot(
    TELEGRAM_BOT_API_TOKEN, exception_handler=ExceptionHandler(), parse_mode="markdown"
)
bot.setup_middleware(ChatMiddleware())

# Create folder for messages models if it not exists
if not os.path.exists(MESSAGES_SAMPLES_DIR):
    os.makedirs(MESSAGES_SAMPLES_DIR)


@bot.my_chat_member_handler()
async def join_message(message: types.ChatMemberUpdated):
    if message.new_chat_member.status == "member":
        try:
            # Send welcome message if bot was added to a group chat
            await bot.send_message(message.chat.id, Reply.ON_START)
        except Exception as e:
            logger.warning(
                f"Could not sent welcome message in chat {message.chat.id} (maybe writing is restricted?): {e}"
            )


@bot.message_handler(func=partial(command_handler, command=Command.START))
async def start(message: types.Message):
    await bot.send_message(message.chat.id, Reply.ON_START)


@bot.message_handler(func=partial(command_handler, command=Command.HELP))
async def help(message: types.Message):
    await bot.send_message(message.chat.id, Reply.ON_HELP)


@bot.message_handler(func=partial(command_handler, command=Command.GENERATE))
async def generate(message: types.Message):
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
        await bot.send_message(message.chat.id, sentence)
    else:  # Not enough samples to generate message
        logger.warning(
            f"Generate command failed for chat {message.chat.id}: not enough messages"
        )
        await bot.send_message(message.chat.id, Reply.ON_MESSAGES_DB_TOO_SMALL)


@bot.message_handler(func=lambda _: True, content_types=["text"])
async def collect(message: types.Message):
    chat_id = message.chat.id

    # Message is only collected when it is sent in group or superchat
    if message.chat.type not in ["group", "superchat"]:
        return

    if chat_id in MESSAGES:
        MESSAGES[chat_id].append(message.text)
    else:
        MESSAGES[chat_id] = [message.text]


async def flush_messages():
    """
    Flushes `MESSAGES` dict to the storage at specified interval
    """
    while True:
        if len(MESSAGES) != 0:
            logger.info(f"Flushing messages into storage: {MESSAGES}")
            for chat_id, messages in MESSAGES.items():
                storage = MessagesStorage(chat_id)
                await storage.push(messages)

            MESSAGES.clear()

        await asyncio.sleep(MESSAGES_FLUSH_INTERVAL)


async def scheduler():
    """
    Runs `aioschedule` tasks in specified interval
    """
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    logger.info("Started Telegram polling and async schedulers")
    await asyncio.gather(
        set_bot_commands(bot), scheduler(), flush_messages(), bot.infinity_polling()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopping polling by user request")
        sys.exit(0)
