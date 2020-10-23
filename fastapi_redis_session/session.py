import pickle
from typing import Any

from redis import Redis

from .config import config


class SessionStorage:
    def __init__(self):
        self.client = Redis.from_url(config.redisURL)

    def __getitem__(self, key: str):
        raw = self.client.get(key)
        return raw and pickle.loads(raw)

    def __setitem__(self, key: str, value: Any):
        self.client.set(key, pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL), ex=config.expireTime)

    def __delitem__(self, key: str):
        self.client.delete(key)

    def genSessionId(self) -> str:
        sessionId = config.genSessionId()
        while self.client.get(sessionId):
            sessionId = config.genSessionId()
        return sessionId
