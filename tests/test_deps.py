from typing import Any
from unittest import mock

import pytest
from fastapi import Depends, FastAPI, Request, Response
from fastapi.testclient import TestClient
from fastapi_redis_session import getSession, setSession
from fastapi_redis_session.deps import getSessionStorage
from fastapi_redis_session.session import SessionStorage
from fastapi_redis_session.config import config


@pytest.fixture
def sessionStorage():
    with mock.patch("fastapi_redis_session.deps.SessionStorage") as mockClass:
        mockStorage = mock.Mock(spec=SessionStorage)
        mockStorage.__setitem__ = mock.Mock()
        mockStorage.__getitem__ = mock.Mock()
        mockClass.return_value = mockStorage
        yield mockStorage


@pytest.fixture
def app(sessionStorage: SessionStorage):
    application = FastAPI(title=__name__)

    @application.post("/setSession")
    async def _setSession(
        request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage)
    ):
        sessionData = await request.json()
        setSession(response, sessionData, sessionStorage)

    @application.get("/getSession")
    async def _setSession(session: Any = Depends(getSession)):
        return session

    yield application


def testDeps(app: FastAPI, sessionStorage):
    client = TestClient(app)
    client.post("/setSession", json=dict(a=1, b="data", c=True))
    sessionStorage.__setitem__.assert_called_once_with(sessionStorage.genSessionId(), dict(a=1, b="data", c=True))

    sessionStorage.__getitem__.return_value = dict(a=1, b="data", c=True)
    client.get("/getSession", cookies={config.sessionIdName: "ssid"})
    sessionStorage.__getitem__.assert_called_once_with("ssid")
