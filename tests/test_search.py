from unittest.mock import AsyncMock, patch

import pytest
from telethon import TelegramClient

from tegracli.main import dispatch_search


@pytest.fixture
def queries():
    return ["randomstring"]


@pytest.mark.asyncio
async def test_search(queries: list[str]):

    client = AsyncMock(TelegramClient)

    print("Hello!", client)

    try:
        client.loop.run_until_complete(dispatch_search(queries, client))
        # with client:
    except Exception:
        assert False
