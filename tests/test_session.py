import datetime
import pickle
from unittest import mock

import pytest
from redis.asyncio import Redis

from fastapi_redis_session.session import SessionStorage


@pytest.fixture
def sessionStorage():
    storage = object.__new__(SessionStorage)
    storage.client = mock.Mock(spec=Redis)
    storage.client.get = mock.AsyncMock()
    storage.client.set = mock.AsyncMock()
    storage.client.delete = mock.AsyncMock()
    storage.client.exists = mock.AsyncMock()
    return storage


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def testSessionStorage(sessionStorage: SessionStorage):
    data = dict(a=1, b="data", c=True)
    sessionStorage.client.exists = mock.AsyncMock(side_effect=[True, False])
    sessionId = await sessionStorage.genSessionId()

    await sessionStorage.set(sessionId, data)
    sessionStorage.client.set.assert_awaited_once_with(
        sessionId, pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL), ex=datetime.timedelta(seconds=21600)
    )

    sessionStorage.client.get = mock.AsyncMock(return_value=pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))
    assert await sessionStorage.get(sessionId) == data
    sessionStorage.client.get.assert_awaited_once_with(sessionId)

    await sessionStorage.delete(sessionId)
    sessionStorage.client.delete.assert_awaited_once_with(sessionId)
    sessionStorage.client.exists.assert_awaited()
