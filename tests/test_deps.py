from typing import Any
from unittest import mock

import pytest
from fastapi import Depends, FastAPI, Request, Response
from fastapi.testclient import TestClient
from fastapi_redis_session import SessionStorage, deleteSession, getSession, getSessionId, getSessionStorage, setSession
from fastapi_redis_session.config import config


@pytest.fixture
def sessionStorage():
    with mock.patch("fastapi_redis_session.deps.SessionStorage") as mockClass:
        mockStorage = mock.AsyncMock(spec=SessionStorage)
        mockStorage.genSessionId.return_value = "generated-ssid"
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
        await setSession(response, sessionData, sessionStorage)

    @application.get("/getSession")
    async def _setSession(session: Any = Depends(getSession)):
        return session

    @application.post("/deleteSession")
    async def _deleteSession(
        sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)
    ):
        await deleteSession(sessionId, sessionStorage)
        return None

    yield application


def testDeps(app: FastAPI, sessionStorage):
    client = TestClient(app)
    client.post("/setSession", json=dict(a=1, b="data", c=True))
    sessionStorage.genSessionId.assert_awaited_once_with()
    sessionStorage.set.assert_awaited_once_with("generated-ssid", dict(a=1, b="data", c=True))

    sessionStorage.get.return_value = dict(a=1, b="data", c=True)
    client.get("/getSession", cookies={config.sessionIdName: "ssid"})
    sessionStorage.get.assert_awaited_once_with("ssid")

    client.post("/deleteSession", cookies={config.sessionIdName: "ssid"})
    sessionStorage.delete.assert_awaited_once_with("ssid")
