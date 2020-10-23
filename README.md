# fastapi-redis-session

![CI](https://github.com/duyixian1234/fastapi-redis-session/workflows/CI/badge.svg?branch=master)

A redis-based session backend for Fastapi apps

## Install

```bash
pip install -U fastapi-redis-session
```

## Use

```python
from typing import Any

from fastapi import Depends, FastAPI, Request, Response

from fastapi_redis_session import deleteSession, getSession, getSessionId, getSessionStorage, setSession, SessionStorage

app = FastAPI(title=__name__)


@app.post("/setSession")
async def _setSession(
    request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage)
):
    sessionData = await request.json()
    setSession(response, sessionData, sessionStorage)


@app.get("/getSession")
async def _setSession(session: Any = Depends(getSession)):
    return session


@app.post("/deleteSession")
async def _deleteSession(
    sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)
):
    deleteSession(sessionId, sessionStorage)
    return None

```

## Config

### Deafult Config

- url of Redis: redis://localhost:6379/0
- name of sessionId: ssid
- generator function of sessionId: `lambda :uuid.uuid4().hex`
- expire time of session in redis: 6 hours

### Custom Config

```python
from fastapi_redis_session.config import basicConfig
basicConfig(
    redisURL="redis://localhost:6379/1",
    sessionIdName="sessionId",
    sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
    expireTime=timedelta(days=1),
    )
```
