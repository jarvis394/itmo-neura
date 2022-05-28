from typing import List
from telebot import types
from config.bot import bot
from lib.command import Command


async def set_bot_commands(commands: List[Command]):
    """
    Sets bot's commands
    """
    bot_commands = list(map(lambda x: types.BotCommand(x.name, x.description), commands))
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=bot_commands,
        scope=types.BotCommandScopeAllGroupChats(),
    )
    await bot.set_my_commands(
        commands=[
            types.BotCommand("start", "Starts your interaction with bot"),
        ],
        scope=types.BotCommandScopeAllPrivateChats(),
    )
