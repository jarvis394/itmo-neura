import os
from typing import List
from aiofile import async_open
from config.bot import MESSAGES
from config.constants import MESSAGES_SAMPLES_DIR
from utils.format import unescape_string, escape_string


def parse_raw(raw: str) -> List[str]:
    result = []
    start = 0

    for i in range(len(raw)):
        if i != 0:
            if raw[i] == ";" and raw[i - 1] != "\\":
                result.append(raw[start:i])

                start = i + 1

    return [unescape_string(message) for message in result]


class MessagesStorage:
    chat_id: int
    pathname: str

    def __init__(self, id: int) -> None:
        filename = str(id)
        pathname = os.path.join(MESSAGES_SAMPLES_DIR, filename + ".raw")
        self.chat_id = id
        self.pathname = pathname

    async def push(self, messages: List[str]) -> int:
        write_mode = "w" if not os.path.exists(self.pathname) else "a"

        # Messages folder should always be present as it is being created at the
        # start of the application
        async with async_open(self.pathname, write_mode, encoding="utf-8") as f:
            line = ";".join([escape_string(message) for message in messages])
            return await f.write(line + ";")

    async def count(self) -> int:
        return len(await self.get())

    async def get(self) -> List[str]:
        inmemory_messages = MESSAGES.get(self.chat_id) or []
        try:
            async with async_open(self.pathname, "r", encoding="utf-8") as f:
                raw = await f.read()
            return parse_raw(raw) + inmemory_messages
        except FileNotFoundError:
            return inmemory_messages

    async def wipe(self) -> bool:
        try:
            os.remove(self.pathname)
            return True
        except:
            return False
