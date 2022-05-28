from config.replies import Reply
from config.bot import bot
from telebot import types
from loguru import logger
from lib.middleware import Middleware


class GroupJoinMiddleware(Middleware):
    name = "GroupJoinMiddleware"

    def __init__(self) -> None:
        self.update_types = ["my_chat_member"]

    async def pre_process(self, message: types.ChatMemberUpdated, data):
        if message.new_chat_member.status == "member":
            try:
                # Send welcome message if bot was added to a group chat
                await bot.send_message(message.chat.id, Reply.ON_START)
            except Exception as e:
                logger.warning(
                    f"Could not sent welcome message in chat {message.chat.id} (maybe writing is restricted?): {e}"
                )

    async def post_process(self, message, data, exception):
        pass
