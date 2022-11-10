"""Define type and function interfaces
"""
from typing import Awaitable, Callable

import telethon

MessageHandler = Callable[[telethon.types.Message], Awaitable[None]]
AuthenticationHandler = Callable[[telethon.TelegramClient], Awaitable[None]]
