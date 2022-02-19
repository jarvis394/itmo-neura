from typing import List, Optional
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from .models import Chat


class ChatCRUD:
    def __init__(self, session: Session):
        self.db = session

    async def get_chat(self, id: int) -> Chat:
        """
        Gets chat object from DB by its ID
        """
        chat = await self.db.query(select(Chat)).filter(Chat.id == id).first()
        return chat

    async def create_chat(
        self,
        id: int,
        random_messages_interval: Optional[int] = 50,
        disable_auto_send: Optional[bool] = False,
    ):
        """
        Creates chat object in DB
        Parameters:
            id - chat ID
            random_messages_interval - messages count after which a random sentence is generated
            disable_auto_send - disable auto generate every N hours
        """
        new_chat = Chat(
            id=id,
            random_messages_interval=random_messages_interval,
            disable_auto_send=disable_auto_send,
        )
        self.db.add(new_chat)
        await self.db.flush()

    async def get_all_chats(self) -> List[Chat]:
        q = await self.db.execute(select(Chat).order_by(Chat.id))
        return q.scalars().all()

    async def update_chat(
        self,
        id: int,
        random_messages_interval: Optional[int],
        disable_auto_send: Optional[bool],
    ):
        """
        Updates chat object in DB
        Parameters:
            id - chat ID
            random_messages_interval - messages count after which a random sentence is generated
            disable_auto_send - disable auto generate every N hours
        """
        q = update(Chat).where(Chat.id == id)

        if random_messages_interval:
            q = q.values(random_messages_interval=random_messages_interval)
        if disable_auto_send:
            q = q.values(disable_auto_send=disable_auto_send)

        q.execution_options(synchronize_session="fetch")
        await self.db.execute(q)
