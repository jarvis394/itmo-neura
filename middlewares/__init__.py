from typing import List
from lib.middleware import Middleware

# Import all middlewares in the folder here
from .chat import ChatMiddleware
from .mention import MentionMiddleware
from .reply import ReplyMiddleware
from .group_join import GroupJoinMiddleware
from .collect import CollectMiddleware
from .counter import CounterMiddleware
from .documents import DocumentsMiddleware
from .callback_query import CallbackQueryMiddleware

MIDDLEWARES: List[Middleware] = [
    ChatMiddleware,
    MentionMiddleware,
    ReplyMiddleware,
    GroupJoinMiddleware,
    CollectMiddleware,
    CounterMiddleware,
    DocumentsMiddleware,
    CallbackQueryMiddleware,
]
