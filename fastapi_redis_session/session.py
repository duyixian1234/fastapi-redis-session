import pickle
from typing import Any

from redis import Redis

from .config import config

try:
    from importlib.metadata import PackageNotFoundError, version as get_version
except ImportError:  # Python < 3.8
    try:
        from importlib_metadata import PackageNotFoundError, version as get_version  # type: ignore
    except ImportError:

        class PackageNotFoundError(Exception):  # type: ignore
            pass

        def get_version(_name: str) -> str:
            raise PackageNotFoundError(_name)


class SessionStorage:
    def __init__(self):
        self.client = Redis.from_url(config.redisURL)
        self._add_driver_info(self.client)

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

        # Try to use DriverInfo class
        try:
            from redis import DriverInfo

            driver_info = DriverInfo().add_upstream_driver("fastapi-redis-session", session_version)
            connection_pool.connection_kwargs["driver_info"] = driver_info
        except (ImportError, AttributeError):
            # Fallback: use lib_name/lib_version
            # Format: lib_name='redis-py(fastapi-redis-session_v{version})'
            connection_pool.connection_kwargs["lib_name"] = f"redis-py(fastapi-redis-session_v{session_version})"
            # lib_version should be the redis client version
            try:
                import redis as redis_module

                redis_version = redis_module.__version__
            except (ImportError, AttributeError):
                redis_version = "unknown"
            connection_pool.connection_kwargs["lib_version"] = redis_version
