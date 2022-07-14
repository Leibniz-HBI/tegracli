from typing import Callable
import pytest
from unittest.mock import patch
from telethon import TelegramClient
from tegracli.main import dispatch_search

@pytest.fixture
def client() -> TelegramClient:
    class MockClient(object):

        # noinspection PyMissingConstructor
        def __init__(self):
            pass

        @property
        def _sender(self, **args):
            print(**args)
        
        def __enter__(self):
            print('enter hit')

        def __exit__(self, a, b, c):
            print('exit hit', a, b, c)

        async def run_until_disconnected(self, func: Callable[[any], any]):
            """ This method can be used to inspect the constructed func that is
            passed in and to assert on that inspection.
            """
            func()
            pass

        async def iter_messages(self: 'TelegramClient', entity: 'hints.EntityLike', limit: float = None, *, offset_date: 'hints.DateLike' = None, offset_id: int = 0, max_id: int = 0, min_id: int = 0, add_offset: int = 0, search: str = None, filter: 'typing.Union[types.TypeMessagesFilter, typing.Type[types.TypeMessagesFilter]]' = None, from_user: 'hints.EntityLike' = None, wait_time: float = None, ids: 'typing.Union[int, typing.Sequence[int]]' = None, reverse: bool = False, reply_to: int = None, scheduled: bool = False) -> 'typing.Union[_MessagesIter, _IDsIter]':
            return {}

    return MockClient()

@pytest.fixture
def queries():
    return ['randomstring']

@patch("telethon.TelegramClient")
def test_search(client: TelegramClient, queries: list[str]):
    try:        
        with client:
            client.run_until_disconnected(dispatch_search(queries, client))
    except Exception:
        assert False
