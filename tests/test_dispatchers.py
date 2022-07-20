from asyncio import AbstractEventLoop
from pathlib import Path
from unittest.mock import Mock
import pytest

from telethon import TelegramClient
import yaml
from tegracli.main import dispatch_search, dispatch_get


@pytest.fixture
def queries():
    return ["randomstring"]


@pytest.fixture
def client():
    with Path('tegracli.conf.yml').open('r') as conf:
        conf = yaml.safe_load(conf)

    return TelegramClient(conf["session_name"], conf["api_id"], conf["api_hash"])


@pytest.mark.api
@pytest.mark.enable_socket
def test_search(queries: list[str], client: TelegramClient):

    # client = Mock(TelegramClient)
    # client.loop = Mock(AbstractEventLoop)
    with client:
        client.loop.run_until_complete(dispatch_search(queries, client))
    # client.assert_called()


@pytest.mark.api
@pytest.mark.enable_socket
def test_get(queries: list[str], client: TelegramClient):

    # client = Mock(TelegramClient)
    # client.loop = Mock(AbstractEventLoop)
    with client:
        client.loop.run_until_complete(dispatch_get(queries, client, {}))
