from datetime import timedelta
from typing import Callable, Optional
from uuid import uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def genSessionId() -> str:
    return uuid4().hex


SessionIdGenerator = Callable[[], str]


def defaultSettings() -> dict[str, SessionIdGenerator]:
    return {"sessionIdGenerator": genSessionId}


class Config(BaseSettings):
    redisURL: str = "redis://localhost:6379/0"
    sessionIdName: str = "ssid"
    expireTime: timedelta = timedelta(hours=6)
    settings: dict[str, SessionIdGenerator] = Field(default_factory=defaultSettings)

    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    def genSessionId(self) -> str:
        return self.settings["sessionIdGenerator"]()


config = Config()


def basicConfig(
    redisURL: Optional[str] = "",
    sessionIdName: Optional[str] = "",
    sessionIdGenerator: Optional[SessionIdGenerator] = None,
    expireTime: Optional[timedelta] = None,
):
    if redisURL:
        config.redisURL = redisURL
    if sessionIdName:
        config.sessionIdName = sessionIdName
    if sessionIdGenerator:
        config.settings["sessionIdGenerator"] = sessionIdGenerator
    if expireTime:
        config.expireTime = expireTime
