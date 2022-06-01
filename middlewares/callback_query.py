from telebot import types
from config.actions import Action
from config.replies import Reply
from lib.middleware import Middleware
from config.states import states
from lib.state_manager import UserState
from config.bot import bot


class CallbackQueryMiddleware(Middleware):
    name = "CallbackQueryMiddleware"

    def __init__(self) -> None:
        self.update_types = ["callback_query"]

    async def pre_process(self, message: types.CallbackQuery, data):
        state_key = "user" + str(message.from_user.id)
        state: UserState = states.get(state_key)
        if (
            message.data == Action.CANCEL
            and state
            and state.awaiting_action == Action.UPLOAD
        ):
            states.remove(state_key)
            await bot.answer_callback_query(
                message.id, Reply.ON_COMMAND_CANCELLED_CALLBACK_QUERY
            )
            await bot.edit_message_text(
                chat_id=state.initial_message.chat.id,
                message_id=state.initial_message.id,
                text=Reply.ON_COMMAND_CANCELLED,
                reply_markup=None,
            )

    async def post_process(self, message, data, exception):
        pass
