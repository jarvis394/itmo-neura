from config.constants import (
    MESSAGES_SAMPLES_DIR,
    MESSAGES_FLUSH_INTERVAL,
)
from telebot.asyncio_helper import session_manager
from loguru import logger
from commands import COMMANDS
from config.keys import HOST, PORT, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH
from config.app import app
from config.commands import set_bot_commands
from utils import cancel_tasks, load_commands, load_middlewares
from lib.messages import MessagesStorage
from lib.db.config import engine, Base
from config.bot import bot, MESSAGES
from uvicorn import Config, Server
import aioschedule
import asyncio
import sys
import os
from uvicorn.main import Server


# Create folder for messages models if it not exists
if not os.path.exists(MESSAGES_SAMPLES_DIR):
    os.makedirs(MESSAGES_SAMPLES_DIR)


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
load_middlewares()

# Add commands dynamically
load_commands()


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
        set_bot_commands(COMMANDS),
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
