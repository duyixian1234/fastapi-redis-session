from typing import Callable, Optional
from uuid import uuid4

from pydantic import BaseSettings


def genSessionId() -> str:
    return uuid4().hex


settings = dict(sessionIdGenerator=genSessionId)


class Config(BaseSettings):
    redisURL: str = "redis://localhost:6379/0"
    settings: dict = settings
    sessionIdName: str = "ssid"

    def genSessionId(self) -> str:
        return self.settings["sessionIdGenerator"]()


config = Config()


def basicConfig(
    redisURL: Optional[str] = "",
    sessionIdName: Optional[str] = "",
    sessionIdGenerator: Optional[Callable[[], str]] = None,
):
    if redisURL:
        config.redisURL = redisURL
    if sessionIdName:
        config.sessionIdName = sessionIdName
    if sessionIdGenerator:
        config.settings["sessionIdGenerator"] = sessionIdGenerator
