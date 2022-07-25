import datetime
import sys
import time
from pathlib import Path
from typing import Dict

import click
import ujson
import yaml
from loguru import logger as log
from telethon import TelegramClient
from telethon.errors import FloodWaitError


def get_client(conf: Dict) -> TelegramClient:
    """ Utility function to initialize the TelegramClient from the loaded configuration values.
    """
    session_name = conf["session_name"]
    api_id = conf["api_id"]
    api_hash = conf["api_hash"]

    client = TelegramClient(session_name, api_id, api_hash)
    client.flood_sleep_threshold = 15 * 60

    return client


async def ensure_authentification(client):
    """ Utility function to ensure that the user is authorized.
    If not an interactive prompt for Telegrams 2FA method is shown.
    """
    if not await client.is_user_authorized():
        phone_number = click.prompt("Enter your phone number:")
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, click.prompt("Enter 2FA code: "))


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """ Tegracli!! Retrieve messages from *Te*le*gra*m with a *CLI*!
    """
    if ctx.obj is None:
        ctx.obj = {}

    conf_path = Path("tegracli.conf.yml")

    if not conf_path.exists():
        log.error("Configuration not found. Terminating!")
        sys.exit(127)
    log.debug(f"Starting tegracli with configuration: {str(conf_path.resolve())}")

    with conf_path.open("r", encoding="UTF-8") as config:
        conf = yaml.safe_load(config)

    ctx.obj["credentials"] = conf


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
def get(
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


def str_dict(d: Dict) -> Dict:
    """ Utility function to recursively convert all values in the input dict to strings.
    """
    if type(d) is dict:
        return {k: str_dict(v) for (k, v) in d.items()}
    elif d is None:
        return d
    elif type(d) is list:
        return [str_dict(v) for v in d]
    elif type(d) is datetime.datetime:
        return d.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return str(d)


async def dispatch_get(users, client: TelegramClient, params: Dict):
    await ensure_authentification(client)
    me = await client.get_me()

    log.info(f"Using telegram account of {me.to_dict().get('username')}")

    for user in users:
        try:
            if str.isnumeric(user):
                user = int(user)
            other = await client.get_entity(user)
            o_dict = other.to_dict()

            n = 0
            async for message in client.iter_messages(other, wait_time=10, **params):
                log.debug(f"Received: {other.username}-{message.id}")
                with Path(f"{other.id}.jsonl").open("a", encoding="utf8") as file:
                    m_dict = message.to_dict()
                    m_dict["user"] = o_dict
                    ujson.dump(str_dict(m_dict), file)
                    n += 1
                    file.write("\n")
        except FloodWaitError as err:
            log.error(
                f"FloodWaitError occurred. Waiting for {datetime.timedelta(seconds=err.seconds)} to resume."
            )
            time.sleep(err.seconds)
        except ValueError as err:
            log.error(f"No dice for {user}, because {err}")
            continue
        log.info(f"Fetched {n} messages for {other.to_dict().get('title')}!")
    await client.send_message(
        "me", f"Hello, myself! I\"m done with {', '.join(users)}!"
    )


async def dispatch_search(queries: list[str], client: TelegramClient):
    await ensure_authentification(client)
    me = await client.get_me()
    log.info(f"Using telegram accout of {me.to_dict().get('username')}")
    for query in queries:
        n = 0
        try:
            async for message in client.iter_messages(None, search=query, limit=15):
                with Path(f"{query}.jsonl").open("a", encoding="utf8") as file:
                    m_dict = message.to_dict()
                    ujson.dump(str_dict(m_dict), file)
                    n += 1
                    file.write("\n")
        except ValueError as error:
            log.error(f"No dice for {query}, because {error}")
            continue
        log.info(f"Fetched {n} messages for {query}!")


if __name__ == "main":
    cli({})
