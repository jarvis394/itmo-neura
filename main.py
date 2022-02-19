from typing import Any, Set
from config.constants import (
    MESSAGES_SAMPLES_DIR,
    MESSAGES_FLUSH_INTERVAL,
)
from telebot import types
from loguru import logger
from functools import partial
from commands import COMMANDS
from middlewares import MIDDLEWARES
from config.commands import set_bot_commands
from config.replies import Reply
from utils import is_command
from lib.messages import MessagesStorage
from lib.db.config import engine, Base, async_session
from config.bot import bot, MESSAGES
import aioschedule
import asyncio
import sys
import os


# Add middlewares dynamically
_middlewares_loaded = 0
for MiddlewareClass in MIDDLEWARES:
    middleware_name = MiddlewareClass.name
    _middlewares_loaded += 1
    try:
        bot.setup_middleware(MiddlewareClass())
        logger.success(
            f'Loaded middleware "{middleware_name}" ({_middlewares_loaded}/{len(MIDDLEWARES)})'
        )
    except Exception as e:
        logger.critical(
            f'Could not load middleware "{middleware_name}" (very bad): {e}'
        )
        _middlewares_loaded -= 1

# Add commands dynamically
_commands_loaded = 0
for CommandClass in COMMANDS:
    command_name = CommandClass.name
    c = CommandClass()
    _commands_loaded += 1
    try:
        bot.add_message_handler(
            bot._build_handler_dict(c.exec, func=partial(is_command, command=c))
        )
        logger.success(
            f"Loaded command /{command_name} ({_commands_loaded}/{len(COMMANDS)})"
        )
    except Exception as e:
        logger.critical(f'Could not load command "{command_name}" (very bad): {e}')
        _commands_loaded -= 1

# Create folder for messages models if it not exists
if not os.path.exists(MESSAGES_SAMPLES_DIR):
    os.makedirs(MESSAGES_SAMPLES_DIR)


# TODO: make handlers be in a folder alongside with commands
# and commands should be executed in bot.message_handler
# which listens for all messages
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


@bot.message_handler(func=lambda _: True, content_types=["text"])
async def collect(message: types.Message):
    chat_id = message.chat.id

    # Message is only collected when it is sent in group or superchat
    if message.chat.type not in ["group", "superchat"]:
        return

    # Message is only collected when it consists at least of 2 words
    if len(message.text.split(" ")) < 2:
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


async def db_setup():
    """
    Sets up DB tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def scheduler():
    """
    Runs `aioschedule` tasks in specified interval
    """
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


def _cancel_tasks(
    to_cancel: Set[asyncio.Task[Any]], loop: asyncio.AbstractEventLoop
) -> None:
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    # In order to cancel all tasks, we need to run them again
    loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            logger.error(
                f"Got an exception on trying to cancel async task: {task.exception()}"
            )
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


async def main():
    logger.info("Started Telegram polling and async schedulers")
    await asyncio.gather(
        set_bot_commands(bot),
        db_setup(),
        scheduler(),
        flush_messages(),
        bot.polling(non_stop=True),
    )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    main_task = loop.create_task(main())

    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Stopping bot by user request...")
        _cancel_tasks({main_task, *asyncio.all_tasks(loop)}, loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)
        sys.exit(0)
