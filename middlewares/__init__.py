from typing import List
from telebot.asyncio_handler_backends import BaseMiddleware

# Import all middlewares in the folder here
from .chat import ChatMiddleware

MIDDLEWARES: List[BaseMiddleware] = [
    ChatMiddleware
]
