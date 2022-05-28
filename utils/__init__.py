from functools import partial
from typing import Any, Set
from commands import COMMANDS
from config.constants import BOT_MENTION_PREFIX, BOT_PREFIX
from telebot import types
from lib.command import Command
from loguru import logger
import asyncio
from config.bot import bot
from middlewares import MIDDLEWARES


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


def load_middlewares():
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


def load_commands():
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
