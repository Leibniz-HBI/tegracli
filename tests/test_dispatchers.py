"""Dispatcher Functions Tests.

This tests suit concerns itself with the asynchronous dispatcher functions.

These tests should be marked both api and socket enabled, since we actually want data from Telegram.
This has the implication that we need valid credentials in a valid `tegracli.conf.yml`.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=wrong-import-position

from pathlib import Path
from typing import Dict, List

import pytest
import ujson
import yaml
from telethon import TelegramClient

from tegracli.dispatch import dispatch_hydrate
from tegracli.main import dispatch_get, dispatch_search


@pytest.fixture
def queries():
    """Random query strings."""
    return ["randomstring"]


@pytest.fixture
def client():
    """Get a configured client."""
    with Path("tegracli.conf.yml").open("r", encoding="utf8") as conf:
        conf = yaml.safe_load(conf)

    return TelegramClient(conf["session_name"], conf["api_id"], conf["api_hash"])


@pytest.mark.api
@pytest.mark.enable_socket
def test_search(queries: List[str], client: TelegramClient):
    """Should run a search on the specified queries.

    Asserts:
        - Should not throw exception
    """
    with client:
        client.loop.run_until_complete(dispatch_search(queries, client))


@pytest.mark.api
@pytest.mark.enable_socket
@pytest.mark.parametrize(
    "params",
    [{"limit": 1}, {"limit": 2, "reverse": True}, {"offset_id": 5, "limit": 1}],
)
@pytest.mark.parametrize("queries", [["channelnotfound123"], ["channel", "1446651076"]])
def test_get(queries: List[str], client: TelegramClient, params: Dict):
    """Should get message for existing channels.

    Asserts:
    - Should not throw exception
    """
    # client = Mock(TelegramClient)
    # client.loop = Mock(AbstractEventLoop)
    with client:
        client.loop.run_until_complete(dispatch_get(queries, client, params))


@pytest.mark.api
@pytest.mark.enable_socket
@pytest.mark.parametrize(
    "params,results", [["QlobalChange/12182", 12182], ["QlobalChangeEspana/162", 162]]
)
def test_dispatch_hydrate(params: str, results: int, client: TelegramClient):
    """Should get message for existing channels.

    Asserts:
    - Should not throw exception
    """
    print("params", params, "results", results)

    output_file = Path("test_hydrate.jsonl")
    if output_file.exists():
        output_file.unlink()
    channel, post_id = params.split("/")
    post_id = int(post_id)

    with output_file.open("a", encoding="utf-8") as file:
        with client:
            client.loop.run_until_complete(
                dispatch_hydrate(channel, [post_id], file, client)
            )

    with output_file.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                res = ujson.loads(
                    line
                )  # pylint: disable=I1101  # c-extensions-no-member, what we
                # know it's there and that's why we don't want to see it
                assert int(res["id"]) == results
            except ValueError:
                continue
