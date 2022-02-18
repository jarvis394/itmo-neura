from typing import List, Dict
from telebot.async_telebot import AsyncTeleBot, CancelUpdate
from telebot.asyncio_handler_backends import BaseMiddleware

# from commands.start import StartCommand
from config.keys import TELEGRAM_BOT_API_TOKEN
from config.replies import Reply
import telebot
from loguru import logger
from telebot import types
from utils import is_command


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        logger.exception(exception)


# This is used to store messages in memory and then
# flush them into storage when they overflow
MESSAGES: Dict[int, List[str]] = {}

bot = AsyncTeleBot(
    TELEGRAM_BOT_API_TOKEN, exception_handler=ExceptionHandler(), parse_mode="markdown"
)
# bot.setup_middleware(ChatMiddleware())
