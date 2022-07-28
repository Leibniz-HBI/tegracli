"""dispatch functions that dispatch requests to Telethon and MTProto
"""
import datetime
import time
from functools import partial
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, Optional

import telethon
import ujson
from loguru import logger as log
from telethon import TelegramClient
from telethon.errors import FloodWaitError

from .types import MessageHandler
from .utilities import str_dict


async def dispatch_iter_messages(
    client: TelegramClient, params: Dict, callback: MessageHandler
) -> None:
    """dispatch a a TG-method with callback

    Parameters:
        client : TelegramClient
        params : Dict
        callback : Callable
    """
    async for message in client.iter_messages(wait_time=10, **params):
        await callback(message)


async def dispatch_get(users, client: TelegramClient, params: Dict):
    """get the message history of a specified set of users."""

    async def handle_channel_message(
        message: telethon.types.Message,
        path: Path,
        other: telethon.types.Channel,
        o_dict: Dict,
    ):
        log.debug(f"Received: {other.username}-{message.id}")
        with path.open("a", encoding="utf8") as file:
            m_dict = message.to_dict()
            m_dict["user"] = o_dict
            ujson.dump(str_dict(m_dict), file)  # pylint: disable=c-extension-no-member
            file.write("\n")

    local_account = await client.get_me()

    log.info(f"Using telegram account of {local_account.username}")

    for user in users:
        done = False
        while done is False:
            try:
                if str.isnumeric(user):
                    user = int(user)
                other = await client.get_entity(user)  # see https://limits.tginfo.me/en
                o_dict = other.to_dict()
                get_message_handler = partial(
                    handle_channel_message,
                    path=Path(f"{other.id}.jsonl"),
                    other=other,
                    o_dict=o_dict,
                )

                _params = params.copy()
                _params["entity"] = other

                await dispatch_iter_messages(client, _params, get_message_handler)
            except FloodWaitError as err:
                delta = datetime.timedelta(seconds=err.seconds)
                log.error(f"FloodWaitError occurred. Waiting for {delta} to resume.")
                time.sleep(err.seconds)
                continue
            except ValueError as err:
                log.error(f"No dice for {user}, because {err}")
                done = True
                continue
            done = True


async def dispatch_search(queries: list[str], client: TelegramClient):
    """dispatch a global search"""
    local_account = await client.get_me()
    log.info(f"Using telegram accout of {local_account.username}")
    for query in queries:
        try:
            async for message in client.iter_messages(None, search=query, limit=15):
                with Path(f"{query}.jsonl").open("a", encoding="utf8") as file:
                    m_dict = message.to_dict()
                    ujson.dump(  # pylint: disable=c-extension-no-member
                        str_dict(m_dict), file
                    )
                    file.write("\n")
        except ValueError as error:
            log.error(f"No dice for {query}, because {error}")
            continue


async def handle_message(message: telethon.types.Message, file: TextIOWrapper):
    """Accept incoming messages and log them to disk

    Parameters
    ----------

    message : telethon.types.Message : incoming single message
    file : TextIOWrapper : opened file to dump the message's json into

    Returns
    -------

    None : nada, nothing
    """
    log.debug(f"Received {message.peer_id.channel_id}/{message.id}")
    ujson.dump(str_dict(message.to_dict()), file)
    file.write("\n")


async def get_input_entity(
    client: TelegramClient, member_id: int
) -> Optional[telethon.types.TypeInputPeer]:
    """wraps the client.get_input_entity function

    Parameters
    ----------

    client : TelegramClient : signed in TG client
    member_id : int : id/handle/URL of the entity to get

    Returns
    -------
    Optional[telethon.types.TypeInputPeer] : returns the requested entity or None
    """
    return await client.get_input_entity(member_id)


async def get_profile(
    client: TelegramClient, member: str, group_name: str
) -> Optional[Dict]:
    """Returns a Dict from the requested entity

    Parameters
    ----------

    client : TelegramClient : signed in TG client
    member : str : id/handle/URL of the entity to request
    """
    _member = int(member) if str.isnumeric(member) else member
    try:
        profile = await client.get_entity(_member)
    except ValueError:
        log.warning(f"Entity for {member} was not found.")
        return None
    p_dict = str_dict(profile.to_dict())
    with (Path(group_name) / "profiles.jsonl").open("a") as profiles:
        ujson.dump(p_dict, profiles)
        profiles.write("\n")

    return p_dict
