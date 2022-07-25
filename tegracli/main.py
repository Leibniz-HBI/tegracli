"""Tegracli's click structure live here.

2022, Philipp Kessling, Leibniz-Institute for Media Research
"""
import sys
from pathlib import Path
from typing import List

import click
import yaml
from loguru import logger as log
from telethon import TelegramClient

from .dispatch import dispatch_get, dispatch_search
from .utilities import ensure_authentication, get_client


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Tegracli!! Retrieve messages from *Te*le*gra*m with a *CLI*!"""

    async def handle_auth(client: TelegramClient):
        phone_number = click.prompt("Enter your phone number:")
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, click.prompt("Enter 2FA code: "))

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

    client.loop.run_until_complete(ensure_authentication(client, handle_auth))


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
@click.option("--reply_to", "-r", help="Only messages replied to specific post id.")
@click.argument("channels", nargs=-1)
@click.pass_context
def get(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    limit: int or None,
    offset_date: str or None,
    offset_id: str or None,
    min_id: int or None,
    max_id: int or None,
    add_offset: int or None,
    from_user: str or None,
    reverse: bool,
    reply_to: str or None,
    channels: list[str],
) -> None:
    """Get messages for the specified channels by either ID or username."""
    client = get_client(ctx.obj["credentials"])

    params = {}
    if limit is not None:
        params["limit"] = None if limit == -1 else limit
    if offset_date is not None:
        params["offset_date"] = offset_date
    if offset_id is not None:
        params["offset_id"] = offset_id
    if max_id is not None:
        params["max_id"] = max_id
    if min_id is not None:
        params["min_id"] = min_id
    if add_offset is not None:
        params["add_offset"] = add_offset
    if from_user is not None:
        params["from_user"] = from_user
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
    "--read_file", "-f", type=click.Path(), help="read account list from file"
)
@click.argument("name", type=str, nargs=1, required=True)
@click.argument("accounts", type=str, nargs=-1)
def init(read_file: Path or None, name: str, accounts: List[str]):
    """initialize a new account group"""
    cwd = Path()
    results_diretory = cwd / name
    account_group = []

    # check whether the directory we try to create is already there.
    if results_diretory.exists():
        log.error(f"{results_diretory} already exists. Aborting.")
        sys.exit(127)

    # copy entries to account group
    if accounts is not None and len(accounts) >= 1:
        for entry in accounts:
            account_group.append(entry)

    if read_file is not None:
        # check whether that file exists:
        if not read_file.exists():
            log.error(f"Cannot read non-existent file {read_file}. Aborting.")
            sys.exit(127)
        else:
            with read_file.open("r") as file:
                for line in file.readlines():
                    account_group.append(line)


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


if __name__ == "main":
    cli({})
