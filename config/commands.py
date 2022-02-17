from telebot.async_telebot import AsyncTeleBot
from telebot import types


class Command:
    COUNT = ["count"]
    GENERATE = ["g", "gen", "generate", "г"]
    HELP = ["help", "помощь"]
    START = ["start"]


async def set_bot_commands(bot: AsyncTeleBot):
    # TODO: dynamically generate bot commands
    """
    Sets bot's commands. Keep in sync with actual commands.
    """
    await bot.delete_my_commands()
    await bot.set_my_commands(
        commands=[
            types.BotCommand(
                "generate", "Generates a random message based on chat history"
            ),
            types.BotCommand("help", "Sends bot's commands"),
        ],
        scope=types.BotCommandScopeAllGroupChats(),
    )
    await bot.set_my_commands(
        commands=[
            types.BotCommand("start", "Starts your interaction with bot"),
        ],
        scope=types.BotCommandScopeAllPrivateChats(),
    )
