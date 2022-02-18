from config.constants import BOT_MENTION_PREFIX, BOT_PREFIX
from telebot import types
from lib.command import Command


def is_command(message: types.Message, command: Command):
    """
    Custom message checker that activates on mention or slash commands

    Example:
    /start or @mention_prefix start or @mention_prefix, start
    """
    text = message.text.strip()
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
