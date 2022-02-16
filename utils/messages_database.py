import os
import mc
from aiofile import async_open
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from config.replies import Reply
from config.constants import MESSAGES_MODELS_DIR


def get_pathname_for_messages_model(message: types.Message):
    filename = str(message.chat.id)
    pathname = os.path.join(MESSAGES_MODELS_DIR, filename + ".txt")
    return pathname


async def collect_message(message: types.Message) -> int:
    pathname = get_pathname_for_messages_model(message)
    text = message.text.replace("\n", ". ").replace("\n\n", ". ") + ","
    write_mode = "w" if not os.path.exists(pathname) else "a"

    # Temp folder should always be present as it is being created at the
    # start of the application
    async with async_open(pathname, write_mode, encoding="utf-8") as f:
        return await f.write(text)


async def generate_sentence(message: types.Message) -> str:
    """
    Generates sentence from group messages model
    Raises:
        - Exception if was not able to generate sentence
    """
    pathname = get_pathname_for_messages_model(message)

    if not os.path.exists(pathname):
        raise Exception(Reply.ON_MESSAGES_DB_NOT_EXIST)

    async with async_open(pathname, "r", encoding="utf-8") as f:
        text: str = await f.read()
        text_model = [sample.strip() for sample in text.split(",")]
    generator = mc.PhraseGenerator(samples=text_model)
    result_text = generator.generate_phrase_or_none(
        attempts=20,
        validators=[mc.validators.words_count(minimal=1, maximal=15)],
        formatters=[mc.formatters.usual_syntax],
    )

    # Generator did not generate the string due to lack of model data, notify user
    if not result_text:
        raise Exception(Reply.ON_MESSAGES_DB_TOO_SMALL)

    return result_text
