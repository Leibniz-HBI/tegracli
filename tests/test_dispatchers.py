""" # Dispatcher Functions Test

This tests suit concerns itself with the asynchronous dispatcher functions.

These tests should be marked both api and socket enabled, since we actually want data from Telegram.
This has the implication that we need valid credentials in a valid `tegracli.conf.yml`.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=wrong-import-position

from pathlib import Path
from typing import Dict

import pytest
import yaml
from telethon import TelegramClient

from tegracli.main import dispatch_get, dispatch_search


@pytest.fixture
def queries():
    """random query strings"""
    return ["randomstring"]


@pytest.fixture
def client():
    """Get a configured client"""
    with Path("tegracli.conf.yml").open("r", encoding="utf8") as conf:
        conf = yaml.safe_load(conf)

    return TelegramClient(conf["session_name"], conf["api_id"], conf["api_hash"])


@pytest.mark.api
@pytest.mark.enable_socket
def test_search(queries: list[str], client: TelegramClient):
    """Should run a search on the specified queries

    Asserts
    -------

    Should not throw exception
    """

    # client = Mock(TelegramClient)
    # client.loop = Mock(AbstractEventLoop)
    with client:
        client.loop.run_until_complete(dispatch_search(queries, client))
    # client.assert_called()


@pytest.mark.api
@pytest.mark.enable_socket
@pytest.mark.parametrize(
    "params",
    [{"limit": 1}, {"limit": 2, "reverse": True}, {"offset_id": 5, "limit": 1}],
)
@pytest.mark.parametrize("queries", [["channelnotfound123"], ["channel", "1446651076"]])
def test_get(queries: list[str], client: TelegramClient, params: Dict):
    """Should get message for existing channels

    Asserts
    -------

    Should not throw exception
    """
    # client = Mock(TelegramClient)
    # client.loop = Mock(AbstractEventLoop)
    with client:
        client.loop.run_until_complete(dispatch_get(queries, client, params))
