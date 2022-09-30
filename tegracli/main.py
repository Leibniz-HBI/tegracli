"""Tegracli's click structure live here.

2022, Philipp Kessling, Leibniz-Institute for Media Research
"""
import re
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import List, Tuple

import click
import yaml
from loguru import logger as log
from telethon import TelegramClient

from .dispatch import (
    dispatch_get,
    dispatch_iter_messages,
    dispatch_search,
    get_input_entity,
    get_profile,
    handle_message,
)
from .group import Group
from .utilities import ensure_authentication, get_client


@click.group()
@click.option("--debug/--no-debug", default=True)
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """Tegracli!! Retrieve messages from *Te*le*gra*m with a *CLI*!"""

    async def _handle_auth(client: TelegramClient):
        phone_number = click.prompt("Enter your phone number:")
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, click.prompt("Enter 2FA code:"))

    if debug:
        log.add("tegracli.log.json", serialize=True)

    if ctx.obj is None:
        ctx.obj = {}

    conf_path = Path("tegracli.conf.yml")

    if not conf_path.exists():
        log.error("Configuration not found. Terminating!")
        sys.exit(127)
    log.debug(f"Starting tegracli with configuration: {str(conf_path.resolve())}")

    with conf_path.open("r", encoding="UTF-8") as config:
        conf = yaml.safe_load(config)

    client = get_client(conf)

    ctx.obj["credentials"] = conf
    ctx.obj["client"] = client

    client.loop.run_until_complete(ensure_authentication(client, _handle_auth))


@cli.command()
@click.option(
    "--limit", "-l", type=int, default=-1, help="Number of messages to retrieve."
)
@click.option(
    "--offset_date",
    "-O",
    type=click.DateTime(["%Y-%m-%d"]),
    help="Offset retrieval to specific date in YYYY-MM-DD format.",
)
@click.option(
    "--offset_id", "-o", type=int, help="Offset retrieval to a specific post number."
)
@click.option("--min_id", "-m", type=int, help="Minimal post number.")
@click.option("--max_id", "-M", type=int, help="Maximal post number")
@click.option(
    "--add_offset",
    "-a",
    type=int,
    help="Add an offset to the post numbers to be retrieved.",
)
@click.option("--from_user", "-f", help="Only messages from this user.")
@click.option(
    "--reverse/--forward",
    default=True,
    help="Should post numbers count upward or downward. Defaults to forward.",
)
@click.option(
    "--reply_to", "-r", type=int, help="Only messages replied to specific post id."
)
@click.argument("channels", nargs=-1)
@click.pass_context
def get(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    limit: int,
    offset_date: datetime,
    offset_id: int,
    min_id: int,
    max_id: int,
    add_offset: int,
    from_user: str,
    reverse: bool,
    reply_to: int,
    channels: list[str],
) -> None:
    """Get messages for the specified channels by either ID or username."""
    client = get_client(ctx.obj["credentials"])

    params = {}
    if limit is not None:
        params["limit"] = None if limit == -1 else limit
    if offset_date is not None:
        params["offset_date"] = offset_date  # type: ignore
    if offset_id is not None:
        params["offset_id"] = offset_id
    if max_id is not None:
        params["max_id"] = max_id
    if min_id is not None:
        params["min_id"] = min_id
    if add_offset is not None:
        params["add_offset"] = add_offset
    if from_user is not None:
        params["from_user"] = from_user  # type: ignore
    if reply_to is not None:
        params["reply_to"] = reply_to
    params["reverse"] = reverse

    with client:
        client.loop.run_until_complete(dispatch_get(channels, client, params=params))


@cli.group()
def group():
    """Manage account groups"""
    return


@group.command()
@click.option(
    "--read_file",
    "-f",
    type=click.Path(),
    help="read an account list from a file, one handle/id/url per line.",
)
@click.option(
    "--start_date",
    "-s",
    type=click.DateTime(["%Y-%m-%d"]),
    help="Start date for the collection. Must be in YYYY-MM-DD format.",
)
@click.option("--limit", "-l", type=int, help="number of posts fo retrieve in one run")
@click.argument("name", type=str, nargs=1, required=True)
@click.argument("accounts", type=str, nargs=-1)
def init(
    read_file: str,
    start_date: datetime,
    limit: int,
    name: str,
    accounts: List[str],
):
    """initialize a new account group"""
    cwd = Path()
    results_directory = cwd / name
    params = {"limit": limit, "reverse": True}
    if start_date is not None:
        params["offset_date"] = start_date  # type: ignore
    # check whether the directory we try to create is already there.
    if results_directory.exists():
        log.error(f"{results_directory} already exists. Aborting.")
        sys.exit(127)

    # intialize account group
    if isinstance(accounts, tuple):
        accounts = list(accounts)
    if accounts is None:
        accounts = []

    if read_file is not None:
        _read_file = Path(read_file)
        # check whether that file exists:
        if not _read_file.exists():
            log.error(f"Cannot read non-existent file {_read_file}. Aborting.")
            sys.exit(127)

        with _read_file.open("r", encoding="utf8") as file:
            for line in file:
                line = str(line)
                # test whether `line` is a valid id|handle|url
                for match in re.finditer(r"[\w\d]+", line):
                    matched_line = match.group(0)
                    log.debug(f"Found {matched_line}.")
                    accounts.append(matched_line)

    log.debug(f"Found these accounts: {', '.join(accounts)}")

    if len(accounts) >= 1:
        _group = Group(accounts, name, params)
        _group.dump()


@group.command()
@click.argument("groups", nargs=-1)
@click.pass_context
def run(ctx: click.Context, groups: Tuple[str]):
    """load a group configuration and run the groups operations"""
    run_group(ctx.obj["client"], groups)


def run_group(client: TelegramClient, groups: Tuple[str]):
    """runs the required operations for the specified groups."""
    cwd = Path()

    if len(groups) >= 1:
        _groups = list(groups)
        # iterate groups
        for group_name in _groups:
            conf = _guarded_group_load(cwd, group_name)

            # iterate over group members
            for member in conf.members:
                # check whether member is known already and, thus, present in profiles.jsonl
                # if (yes
                #   load user object
                profile = conf.get_member_profile(member)
                # if (no)
                if profile is None:
                    #   load user object from TG and save it to profiles.jsonl
                    profile = client.loop.run_until_complete(
                        get_profile(client, member, group_name)
                    )
                    # check whether profile is also unknown to TG
                    if profile is None:
                        index = conf.members.index(member)
                        conf.members.pop(index)
                        conf.unreachable_members.append(member)
                        continue  # skip this user and commence with the next one
                    #   check whether the member was specified by a handle
                    #   if (yes)
                    if not str.isnumeric(member):
                        #       replace handle by ID
                        index = conf.members.index(member)
                        conf.members[index] = profile["id"]
                        member = profile["id"]
                        conf.dump()

                # get the input_entity from telethon
                entity = client.loop.run_until_complete(
                    get_input_entity(client, int(member))
                )

                # check whether a jsonl-file for this member exists
                # if (yes)
                #   iterate over lines in file and get the highest message.id
                #   modify `params`-dict accordingly
                _params = conf.get_params(entity=entity)
                # Only set the ``min_id`` parameter if a file is existent for the user
                min_id = conf.get_last_message_for(member)
                if min_id is not None:
                    _params["min_id"] = min_id

                log.debug(f"Request with the following parameters: {_params}")

                # request data from telethon and write to disk
                with (Path(group_name) / (member + ".jsonl")).open("a") as member_file:
                    client.loop.run_until_complete(
                        dispatch_iter_messages(
                            client,
                            params=_params,
                            callback=partial(
                                handle_message, file=member_file, injects=None
                            ),
                        )
                    )
            # done.

    else:
        log.info("No group specified.")


def _guarded_group_load(cwd: Path, _name: str) -> Group:
    group_conf_fil = cwd / _name / "tegracli_group.conf.yml"
    if not group_conf_fil.exists():
        log.error(f"Unknown group {_name}. Aborting.")
        sys.exit(127)
    with group_conf_fil.open("r") as file:
        _group: Group = yaml.full_load(file)
        return _group


@cli.command()
@click.argument("queries", nargs=-1)
@click.pass_context
def search(ctx: click.Context, queries: list[str]):
    """This function searches Telegram content that is available to your account
    for the specified search term(s).
    """
    client = get_client(ctx.obj["credentials"])

    with client:
        client.loop.run_until_complete(dispatch_search(queries, client))


# if __name__ == "main":
#     cli({})
