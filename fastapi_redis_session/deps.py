from typing import Any, Generator

from fastapi import Depends, Request, Response

from .config import config
from .session import SessionStorage


def getSessionStorage() -> Generator:
    storage = SessionStorage()
    yield storage


def getSession(request: Request, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    sessionId = request.cookies.get(config.sessionIdName, "")
    return sessionStorage[sessionId]


def setSession(response: Response, session: Any, sessionStorage: SessionStorage):
    sessionId = sessionStorage.genSessionId()
    sessionStorage[sessionId] = session
    response.set_cookie(config.sessionIdName, sessionId, httponly=True)
