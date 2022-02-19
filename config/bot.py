from typing import List, Dict
from telebot.async_telebot import AsyncTeleBot
from config.keys import TELEGRAM_BOT_API_TOKEN
import telebot
from loguru import logger


class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        logger.exception(exception)


# This is used to store messages in memory and then
# flush them into storage when they overflow
MESSAGES: Dict[int, List[str]] = {}

bot = AsyncTeleBot(
    TELEGRAM_BOT_API_TOKEN, exception_handler=ExceptionHandler(), parse_mode="markdown"
)
