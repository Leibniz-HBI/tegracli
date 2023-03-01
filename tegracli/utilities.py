"""Utility functions for tegracli."""
import datetime
from functools import singledispatch
from typing import Any, Dict, Union

from telethon import TelegramClient

from .types import AuthenticationHandler


@singledispatch
def str_dict(data):
    """Utility function to recursively convert all values in the data dict to strings."""
    return data


@str_dict.register(dict)
def _(data: Dict[str, Any]) -> Dict[str, Union[Any, str]]:
    return {k: str_dict(v) for (k, v) in data.items()}


@str_dict.register(list)
def _(data: list) -> list:
    return [str_dict(v) for v in data]


@str_dict.register(datetime.datetime)
def _(data: datetime.datetime) -> str:
    return data.strftime("%Y-%m-%d %H:%M:%S")


@str_dict.register(bytes)
def _(data: bytes) -> str:
    return str(data)


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

    Params:
        client TelegramClient
        callback AuthenticationHandler
    """
    await client.connect()
    if not await client.is_user_authorized():
        await callback(client)
