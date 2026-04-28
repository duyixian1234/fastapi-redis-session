import pickle
import sys
from importlib.metadata import PackageNotFoundError, version as get_version
from typing import Any

import redis as redis_module
from redis.asyncio import Redis

from .config import config


class SessionStorage:
    def __init__(self):
        self.client = Redis.from_url(config.redisURL)
        self._add_driver_info(self.client)

    async def get(self, key: str):
        raw = self.client.get(key)
        raw = await raw
        return raw and pickle.loads(raw)

    async def set(self, key: str, value: Any):
        await self.client.set(key, pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL), ex=config.expireTime)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def genSessionId(self) -> str:
        sessionId = config.genSessionId()
        while await self.client.exists(sessionId):
            sessionId = config.genSessionId()
        return sessionId

    async def close(self) -> None:
        await self.client.aclose()

    @staticmethod
    def _add_driver_info(redis_client) -> None:
        """Add driver identification to Redis connection.

        Uses DriverInfo class if available, or falls back to
        lib_name/lib_version for older versions.
        """
        # Get fastapi-redis-session version
        try:
            session_version = get_version("fastapi-redis-session")
        except PackageNotFoundError:
            session_version = "unknown"

        # Get connection pool from the redis client
        connection_pool: Any = getattr(redis_client, "connection_pool", None)
        if connection_pool is None:
            return

        active_redis_module = sys.modules.get("redis", redis_module)

        # Try to use DriverInfo class
        try:
            driver_info_cls = getattr(active_redis_module, "DriverInfo", None)
            if not callable(driver_info_cls):
                raise AttributeError

            driver_info = driver_info_cls().add_upstream_driver("fastapi-redis-session", session_version)
            connection_pool.connection_kwargs["driver_info"] = driver_info
        except (ImportError, AttributeError):
            # Fallback: use lib_name/lib_version
            # Format: lib_name='redis-py(fastapi-redis-session_v{version})'
            connection_pool.connection_kwargs["lib_name"] = f"redis-py(fastapi-redis-session_v{session_version})"
            # lib_version should be the redis client version
            try:
                redis_version = active_redis_module.__version__
            except (ImportError, AttributeError):
                redis_version = "unknown"
            connection_pool.connection_kwargs["lib_version"] = redis_version
