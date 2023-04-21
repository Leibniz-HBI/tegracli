"""Dispatch functions that request data from Telethon and MTProto."""
import datetime
import sys
import time
from functools import partial
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List, Optional

import telethon
import ujson
from loguru import logger as log
from telethon import TelegramClient
from telethon.errors import (
    ChannelPrivateError,
    FloodWaitError,
    RPCError,
    UserDeactivatedError,
    UsernameNotOccupiedError,
)

from .types import MessageHandler
from .utilities import str_dict

# pylint: disable=I1101  # c-extensions-no-member; we know it's there and that's why we don't
# want to see it


async def dispatch_iter_messages(
    client: TelegramClient, params: Dict, callback: MessageHandler
) -> None:
    """Dispatch a TG-method with callback.

    Args:
        client: the client to use.
        params: the parameters to pass to the method.
        callback: the callback to pass data to.
    """
    try:
        async for message in client.iter_messages(wait_time=10, **params):
            await callback(message)
    except UserDeactivatedError:
        log.error("User account has been deactivated by Telegram. Stopping now.")
        sys.exit(127)
    except UsernameNotOccupiedError:
        log.error(f"Entity {params['entity']} does not exist. Skipping.")
    except ChannelPrivateError:
        log.error(f"Entity {params['entity']} is private. Skipping.")
    except RPCError as err:
        log.error(f"RPCError occurred: {err}")


async def dispatch_get(users, client: TelegramClient, params: Dict):
    """Get the message history of a specified set of users."""
    for user in users:
        done = False
        while done is False:
            try:
                if str.isnumeric(user):
                    user = int(user)
                other = await client.get_entity(user)  # see https://limits.tginfo.me/en
                o_dict = str_dict(other.to_dict())
                _params = params.copy()
                _params["entity"] = other
                with Path(f"{other.id}.jsonl").open("a", encoding="utf8") as file:
                    await dispatch_iter_messages(
                        client,
                        _params,
                        partial(handle_message, file=file, injects={"user": o_dict}),
                    )
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


async def dispatch_hydrate(
    channel: str,
    post_ids: List[str],
    output_file: TextIOWrapper,
    client: TelegramClient,
):
    """Dispatch a hydration by channel_id/post_id."""
    await dispatch_iter_messages(
        client,
        {"entity": channel, "ids": post_ids},
        partial(handle_message, file=output_file, injects=None),
    )


async def dispatch_search(queries: List[str], client: TelegramClient):
    """Dispatch a global search."""
    local_account = await client.get_me()
    log.info(f"Using telegram account of {local_account.username}")
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


async def handle_message(
    message: Optional[telethon.types.Message],
    file: TextIOWrapper,
    injects: Optional[Dict],
):
    """Accept incoming messages and log them to disk.

    Args:
        message: incoming single message.
        file: opened file to dump the message's json into.
        injects: additional data to inject into the message.
    """
    if message is None:
        log.error("Message is None. Skipping.")
        return

    m_dict = str_dict(message.to_dict())
    if injects is not None:
        for key, value in injects.items():
            m_dict[key] = value

    ujson.dump(m_dict, file, ensure_ascii=True)
    file.write("\n")


async def get_input_entity(
    client: TelegramClient, member_id: int
) -> Optional[telethon.types.TypeInputPeer]:
    """Wraps the client.get_input_entity function.

    Args:
        client: signed in TG client.
        member_id: id/handle/URL of the entity to get.

    Returns:
        Optional[telethon.types.TypeInputPeer] : returns the requested entity or None
    """
    return await client.get_input_entity(member_id)


async def get_profile(
    client: TelegramClient, member: str, group_name: str
) -> Optional[Dict[str, str]]:
    """Returns a Dict from the requested entity.

    Args:
        client: signed in TG client.
        member: id/handle/URL of the entity to request.
        group_name: name of the group to save the profile to.
    """
    _member = int(member) if str.isnumeric(member) else member
    profile = await client.get_entity(_member)
    p_dict: Dict[str, str] = str_dict(profile.to_dict())
    with (Path(group_name) / "profiles.jsonl").open("a") as profiles:
        ujson.dump(p_dict, profiles)
        profiles.write("\n")

    return p_dict
