from typing import Any, Set
from config.constants import BOT_MENTION_PREFIX, BOT_PREFIX
from telebot import types
from lib.command import Command
from loguru import logger
import asyncio


def is_command(message: types.Message, command: Command):
    """
    Custom message checker that activates on mention or slash commands

    Example:
    /start or @mention_prefix start or @mention_prefix, start
    """
    if not message or not (message.text or message.caption):
        return False

    text = (message.text or message.caption).strip()
    args = text.split(" ")
    possible_matches = [command.name] + command.aliases

    if len(args) > 1:
        return args[0].startswith(BOT_MENTION_PREFIX) and args[1] in possible_matches
    elif len(args) == 1:
        return args[0].startswith(BOT_PREFIX) and (
            text[len(BOT_PREFIX) :] in possible_matches
            or text[len(BOT_PREFIX) : -len(BOT_MENTION_PREFIX)] in possible_matches
        )
    else:
        return False


def cancel_tasks(
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
