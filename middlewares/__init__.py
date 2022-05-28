from typing import List
from lib.middleware import Middleware

# Import all middlewares in the folder here
from .chat import ChatMiddleware
from .reply import ReplyMiddleware
from .group_join import GroupJoinMiddleware
from .collect import CollectMiddleware

MIDDLEWARES: List[Middleware] = [
    ChatMiddleware,
    ReplyMiddleware,
    GroupJoinMiddleware,
    CollectMiddleware,
]
