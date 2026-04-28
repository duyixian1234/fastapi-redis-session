from typing import Any, AsyncGenerator

from fastapi import Depends, Request, Response

from .config import config
from .session import SessionStorage


async def getSessionStorage() -> AsyncGenerator[SessionStorage, None]:
    storage = SessionStorage()
    try:
        yield storage
    finally:
        await storage.close()


async def getSession(request: Request, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    sessionId = request.cookies.get(config.sessionIdName, "")
    return await sessionStorage.get(sessionId)


def getSessionId(request: Request):
    sessionId = request.cookies.get(config.sessionIdName, "")
    return sessionId


async def setSession(response: Response, session: Any, sessionStorage: SessionStorage) -> str:
    sessionId = await sessionStorage.genSessionId()
    await sessionStorage.set(sessionId, session)
    response.set_cookie(config.sessionIdName, sessionId, httponly=True)
    return sessionId


async def deleteSession(sessionId: str, sessionStorage: SessionStorage):
    await sessionStorage.delete(sessionId)
