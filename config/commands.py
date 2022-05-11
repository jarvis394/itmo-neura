from telebot.async_telebot import AsyncTeleBot
from telebot import types
from config.bot import bot


async def set_bot_commands():
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
            types.BotCommand("count", "Sends a number of saved messages to learn on"),
            types.BotCommand("jpeg", "Sends low-quality jpeg funny"),
            types.BotCommand("demotivate", "Generates random demotivator iamge based on chat history"),
        ],
        scope=types.BotCommandScopeAllGroupChats(),
    )
    await bot.set_my_commands(
        commands=[
            types.BotCommand("start", "Starts your interaction with bot"),
        ],
        scope=types.BotCommandScopeAllPrivateChats(),
    )
