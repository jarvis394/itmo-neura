from commands.count import CountCommand
from config.bot import MESSAGES
from pytest_mock import MockerFixture
from types import SimpleNamespace


command = CountCommand()
chat_id = -1
test_messages = ["foo", "bar"]
mock_message = SimpleNamespace()
mock_message.chat = SimpleNamespace()
mock_message.chat.id = chat_id


async def test_count_adds_on_new_message_to_cache(mocker: MockerFixture) -> None:
    MESSAGES[chat_id] = test_messages

    async def mock_count(self):
        return 0

    async def mock_send_message(_id, message):
        return message

    mocker.patch("utils.messages.MessagesStorage.count", mock_count)
    mocker.patch("config.bot.bot.send_message", mock_send_message)

    assert (
        await command.exec(message=mock_message)
        == f"✨ Сохранено {len(test_messages)} строк для обучения"
    )


async def test_count_adds_on_new_message_to_storage(mocker: MockerFixture) -> None:
    MESSAGES[chat_id] = []

    async def mock_get(self):
        return test_messages

    async def mock_send_message(_id, message):
        return message

    mocker.patch("utils.messages.MessagesStorage.get", mock_get)
    mocker.patch("config.bot.bot.send_message", mock_send_message)

    assert (
        await command.exec(message=mock_message)
        == f"✨ Сохранено {len(test_messages)} строк для обучения"
    )
