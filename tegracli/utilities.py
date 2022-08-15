"""Utility functions for tegracli
"""
import datetime
from typing import Dict

from telethon import TelegramClient

from .types import AuthenticationHandler


def str_dict(data):
    """Utility function to recursively convert all values in the data dict to strings."""
    if isinstance(data, dict):
        return {k: str_dict(v) for (k, v) in data.items()}
    if isinstance(data, list):
        return [str_dict(v) for v in data]
    if isinstance(data, datetime.datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(data, bytes):
        return str(data)
    return data


def get_client(conf: Dict) -> TelegramClient:
    """Utility function to initialize the TelegramClient from the loaded configuration values."""
    session_name = conf["session_name"]
    api_id = conf["api_id"]
    api_hash = conf["api_hash"]

    client = TelegramClient(session_name, api_id, api_hash)
    client.flood_sleep_threshold = 15 * 60

    return client


async def ensure_authentication(
    client: TelegramClient, callback: AuthenticationHandler
):
    """Utility function to ensure that the user is authorized.
    If not an interactive prompt for Telegrams 2FA method is shown.
    """
    await client.connect()
    if not await client.is_user_authorized():
        callback(client)
