from telebot.async_telebot import CancelUpdate
from telebot import types
from commands.jpeg import JpegCommand
from commands.demotivate import DemotivateCommand
from config.actions import Action
from lib.middleware import Middleware
from config.states import states
from lib.state_manager import UserState
from config.bot import bot
from loguru import logger


class DocumentsMiddleware(Middleware):
    name = "DocumentsMiddleware"

    def __init__(self) -> None:
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        state_key = "user" + str(message.from_user.id)
        state: UserState = states.get(state_key)
        has_attachment = bool(message.photo or message.document)

        if has_attachment and state and state.awaiting_action == Action.UPLOAD:
            states.remove(state_key)
            command_name = state.command
            initial_message = state.initial_message

            if command_name == "jpeg":
                command = JpegCommand()
            elif command_name == "demotivate":
                command = DemotivateCommand()

            try:
                await bot.delete_message(initial_message.chat.id, initial_message.id)
            except Exception as e:
                logger.warning(
                    f"Could not delete message {initial_message.id} at chat {initial_message.chat.id}:",
                    e,
                )
            
            await command.send_image(message)
            return CancelUpdate()

    async def post_process(self, message, data, exception):
        pass
