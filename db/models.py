from sqlalchemy import Column, Integer, Boolean
from .config import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    random_messages_interval = Column(Integer, nullable=False, default=50)
    disable_auto_send = Column(Boolean, nullable=False, default=False)
