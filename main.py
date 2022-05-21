from config.constants import (
    MESSAGES_SAMPLES_DIR,
    MESSAGES_FLUSH_INTERVAL,
)
from telebot import types
from telebot.asyncio_helper import session_manager
from loguru import logger
from functools import partial
from commands import COMMANDS
from config.keys import HOST, PORT, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH
from config.app import app
from lib.command import Command
from middlewares import MIDDLEWARES
from config.commands import set_bot_commands
from config.replies import Reply
from utils import is_command, cancel_tasks
from lib.messages import MessagesStorage
from lib.db.config import engine, Base, async_session
from config.bot import bot, MESSAGES
from uvicorn import Config, Server
import aioschedule
import asyncio
import sys
import os
from uvicorn.main import Server


class AppStatus:
    should_exit = False

    @staticmethod
    def handle_exit(*args, **kwargs):
        AppStatus.should_exit = True
        original_handler(*args, **kwargs)


# Monkey patch exit handler for `uvicorn` server
original_handler = Server.handle_exit
Server.handle_exit = AppStatus.handle_exit

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
    c: Command = CommandClass()
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
    Flushes `MESSAGES` dict to the storage
    """
    if len(MESSAGES) != 0:
        logger.info(f"Flushing messages into storage: {MESSAGES}")
        for chat_id, messages in MESSAGES.items():
            storage = MessagesStorage(chat_id)
            await storage.push(messages)

        MESSAGES.clear()


async def scheduler():
    """
    Runs `aioschedule` tasks in specified interval
    """
    while AppStatus.should_exit is False:
        await aioschedule.run_pending()
        await asyncio.sleep(0.1)


async def db_setup():
    """
    Sets up DB tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    logger.info("Started Telegram bot and async schedulers")
    logger.info(f"Started FastAPI webhooks service on port {PORT}")
    config = Config(app=app, loop=asyncio.get_event_loop(), port=PORT, host=HOST)
    server = Server(config)

    aioschedule.every(MESSAGES_FLUSH_INTERVAL).seconds.do(flush_messages).tag(0)

    current_webhook = await bot.get_webhook_info()
    if current_webhook.url != WEBHOOK_URL_BASE + WEBHOOK_URL_PATH:
        await bot.remove_webhook()
        await bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

    await asyncio.gather(
        session_manager.session.close(),  # Fixes aiohttp warning for unclosed session
        db_setup(),
        set_bot_commands(),
        server.serve(),
        scheduler(),
    )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    main_task = loop.create_task(main())

    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error("Caught exception: " + e)
    finally:
        logger.info("Stopping bot by user request...")

        cancel_tasks({main_task, *asyncio.all_tasks(loop)}, loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(session_manager.session.close())
        loop.stop()
        loop.close()
        asyncio.set_event_loop(None)
        sys.exit(0)
