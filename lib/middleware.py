from telebot.asyncio_handler_backends import BaseMiddleware


class Middleware(BaseMiddleware):
    name: str
    """ Middleware name (for pretty-print in console) """
