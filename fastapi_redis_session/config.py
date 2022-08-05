from datetime import timedelta
from typing import Callable, Optional
from uuid import uuid4
from functools import lru_cache
from pydantic import BaseSettings

class Config(BaseSettings):
    redisURL: str
    sessionIdName: str
    sessionIdGenerator: dict
    expireTime: timedelta

    def sessionIdGenerator(self) -> str:
        return sessionIdGenerator()

@lru_cache
def config(
    redisURL: Optional[str] = "redis://localhost:6379/0",
    sessionIdName: Optional[str] = "ssid",
    sessionIdGenerator: Optional[Callable[[], str]] = lambda _: uuid4().hex,
    expireTime: Optional[timedelta] = timedelta(hours=6),
):
    return Config(redisURL, sessionIdName, sessionIdGenerator, expireTime)
