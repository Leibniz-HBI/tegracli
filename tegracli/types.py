"""Define type and function interfaces
"""
from typing import Callable

import telethon

MessageHandler = Callable[[telethon.types.Message], None]
AuthenticationHandler = Callable[[telethon.TelegramClient], None]
