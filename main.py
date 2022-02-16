from config.constants import BOT_MENTION_PREFIX, BOT_PREFIX
from config.keys import HOST, PORT, TELEGRAM_BOT_API_TOKEN
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from loguru import logger
from functools import partial
from config.replies import Reply
import aioschedule
import asyncio
import telebot
import sys


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        logger.exception(exception)


def command_handler(message: types.Message, command: str):
    """
    Custom message handler that activates on mention or slash commands

    Example:
    /start or @mention_prefix start or @mention_prefix, start
    """
    text = message.text.strip()
    args = text.split(" ")

    if len(args) > 1:
        return args[0].startswith(BOT_MENTION_PREFIX) and args[1] == command
    elif len(args) == 1:
        return args[0].startswith(BOT_PREFIX)
    else:
        return False


bot = AsyncTeleBot(TELEGRAM_BOT_API_TOKEN, exception_handler=ExceptionHandler())


@bot.my_chat_member_handler()
async def join_message(message: types.ChatMemberUpdated):
    if message.new_chat_member.status == "member":
        # Send welcome message if bot was added to a group chat
        await bot.send_message(message.chat.id, Reply.ON_GROUP_JOIN)


@bot.message_handler(func=partial(command_handler, command="start"))
async def start(message: types.Message):
    await bot.send_message(message.chat.id, "Hello!")
    raise Exception("oops!")


@bot.message_handler(func=lambda _: True, content_types=["text"])
async def collect(message: types.Message):
    print(message.text)


async def scheduler():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    logger.info("Started Telegram Polling and async scheduler")
    await asyncio.gather(bot.polling(), scheduler())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopping polling by user request")
        sys.exit(0)
