from config.bot import MESSAGES
from telebot import types
from lib.middleware import Middleware


class CollectMiddleware(Middleware):
    name = "CollectMiddleware"

    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        if message.content_type != "text":
            return

        chat_id = message.chat.id

        # Message is only collected when it is sent in group or supergroup
        if message.chat.type not in ["group", "superchat", "supergroup"]:
            return

        # Message is only collected when it has length over 2
        if len(message.text) < 2:
            return

        if chat_id in MESSAGES:
            MESSAGES[chat_id].append(message.text)
        else:
            MESSAGES[chat_id] = [message.text]

    async def post_process(self, message, data, exception):
        pass
