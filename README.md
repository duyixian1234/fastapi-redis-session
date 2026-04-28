# fastapi-redis-session

![CI](https://github.com/duyixian1234/fastapi-redis-session/workflows/CI/badge.svg?branch=master)

A redis-based session backend for Fastapi apps

## Install

```bash
pip install -U fastapi-redis-session
```

Requires Python 3.12 or newer.

The public API is async-only and uses `redis.asyncio`.

## Development

```bash
uv sync --group dev
uv run pytest
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
    await setSession(response, sessionData, sessionStorage)


@app.get("/getSession")
async def _setSession(session: Any = Depends(getSession)):
    return session


@app.post("/deleteSession")
async def _deleteSession(
    sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)
):
    await deleteSession(sessionId, sessionStorage)
    return None

```

`getSession` is an async dependency, and `setSession` / `deleteSession` must be awaited inside async route handlers.

## Example app

Here is a minimal runnable FastAPI example with:

- `POST /login`: log in and write a session
- `GET /me`: read the current user from the session

The example assumes Redis is available locally at `redis://localhost:6379/0`.

```python
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from fastapi_redis_session import SessionStorage, getSession, getSessionStorage, setSession
from fastapi_redis_session.config import basicConfig

basicConfig(redisURL="redis://localhost:6379/0", sessionIdName="ssid")

app = FastAPI(title="fastapi-redis-session example")

FAKE_USER = {
    "username": "alice",
    "password": "secret123",
    "name": "Alice",
    "email": "alice@example.com",
}


class LoginBody(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(
    body: LoginBody,
    response: Response,
    sessionStorage: SessionStorage = Depends(getSessionStorage),
):
    if body.username != FAKE_USER["username"] or body.password != FAKE_USER["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")

    user = {
        "username": FAKE_USER["username"],
        "name": FAKE_USER["name"],
        "email": FAKE_USER["email"],
    }
    session_id = await setSession(response, user, sessionStorage)
    return {"message": "login success", "session_id": session_id, "user": user}


@app.get("/me")
async def me(session: Any = Depends(getSession)):
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not logged in")
    return session
```

Save it as `example.py`, then run:

```bash
uvicorn example:app --reload
```

Test it with `curl`:

1. Log in and save the cookie

```bash
curl -i \
  -X POST http://127.0.0.1:8000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret123"}' \
  -c cookies.txt
```

2. Use the cookie to fetch the current user

```bash
curl -i \
  http://127.0.0.1:8000/me \
  -b cookies.txt
```

3. Test `/me` without logging in

```bash
curl -i http://127.0.0.1:8000/me
```

## Migration notes

- `SessionStorage` now uses `redis.asyncio.Redis`.
- Session access is no longer exposed through sync magic methods; use the async helper functions or awaitable storage methods instead.
- Existing code that called `setSession(...)` or `deleteSession(...)` without `await` must be updated.

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
