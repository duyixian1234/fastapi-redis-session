# fastapi-redis-session

A redis-based session backend for Fastapi apps

## Install

```bash
pip install -U fastapi-redis-session
```

## Use

```python
from typing import Any

from fastapi import Depends, FastAPI, Request, Response

from fastapi_redis_session import getSession, setSession
from fastapi_redis_session.deps import getSessionStorage
from fastapi_redis_session.session import SessionStorage

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

```
