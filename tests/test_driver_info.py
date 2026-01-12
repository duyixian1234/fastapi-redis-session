"""Tests for Redis DriverInfo support in SessionStorage."""

import sys
from unittest.mock import MagicMock, patch

from fastapi_redis_session.session import SessionStorage


class TestDriverInfo:
    """Test suite for Redis driver info functionality."""

    def test_add_driver_info_with_driver_info_class(self):
        """Test _add_driver_info with modern redis-py (DriverInfo class available)."""
        mock_redis = MagicMock()
        mock_pool = MagicMock()
        mock_pool.connection_kwargs = {}
        mock_redis.connection_pool = mock_pool

        # Create a mock DriverInfo instance with add_upstream_driver method
        mock_driver_info_instance = MagicMock()
        mock_driver_info_instance.add_upstream_driver = MagicMock(return_value=mock_driver_info_instance)

        # Create a mock DriverInfo class
        mock_driver_info_class = MagicMock(return_value=mock_driver_info_instance)

        # Create a mock redis module with DriverInfo
        mock_redis_module = MagicMock()
        mock_redis_module.DriverInfo = mock_driver_info_class

        with patch("fastapi_redis_session.session.get_version", return_value="0.2.0"):
            # Temporarily add our mock redis module
            original_redis = sys.modules.get("redis")
            sys.modules["redis"] = mock_redis_module

            try:
                SessionStorage._add_driver_info(mock_redis)

                # Verify driver_info was set in connection_kwargs
                assert "driver_info" in mock_pool.connection_kwargs

                # Verify add_upstream_driver was called with correct arguments
                mock_driver_info_instance.add_upstream_driver.assert_called_once_with("fastapi-redis-session", "0.2.0")
            finally:
                # Restore original redis module
                if original_redis:
                    sys.modules["redis"] = original_redis
                else:
                    sys.modules.pop("redis", None)

    def test_add_driver_info_fallback_old_redis(self):
        """Test _add_driver_info fallback for older redis-py versions (no DriverInfo)."""
        mock_redis = MagicMock()
        mock_pool = MagicMock()
        mock_pool.connection_kwargs = {}
        mock_redis.connection_pool = mock_pool

        # Create a mock redis module WITHOUT DriverInfo but WITH __version__
        mock_redis_module = MagicMock(spec=["__version__"])
        mock_redis_module.__version__ = "3.5.3"

        with patch("fastapi_redis_session.session.get_version", return_value="0.2.0"):
            # Temporarily replace redis module
            original_redis = sys.modules.get("redis")
            sys.modules["redis"] = mock_redis_module

            try:
                SessionStorage._add_driver_info(mock_redis)

                # For older redis-py versions without DriverInfo, should fall back to lib_name and lib_version
                assert "driver_info" not in mock_pool.connection_kwargs
                assert mock_pool.connection_kwargs["lib_name"] == "redis-py(fastapi-redis-session_v0.2.0)"
                assert mock_pool.connection_kwargs["lib_version"] == "3.5.3"
            finally:
                # Restore original redis module
                if original_redis:
                    sys.modules["redis"] = original_redis
                else:
                    sys.modules.pop("redis", None)

    def test_add_driver_info_no_connection_pool(self):
        """Test _add_driver_info when redis client has no connection_pool."""
        mock_redis = MagicMock()
        mock_redis.connection_pool = None

        # Should not raise an exception
        SessionStorage._add_driver_info(mock_redis)

    def test_add_driver_info_unknown_version(self):
        """Test _add_driver_info when version cannot be determined."""
        mock_redis = MagicMock()
        mock_pool = MagicMock()
        mock_pool.connection_kwargs = {}
        mock_redis.connection_pool = mock_pool

        # Create a mock DriverInfo instance with add_upstream_driver method
        mock_driver_info_instance = MagicMock()
        mock_driver_info_instance.add_upstream_driver = MagicMock(return_value=mock_driver_info_instance)

        # Create a mock DriverInfo class
        mock_driver_info_class = MagicMock(return_value=mock_driver_info_instance)

        # Create a mock redis module with DriverInfo
        mock_redis_module = MagicMock()
        mock_redis_module.DriverInfo = mock_driver_info_class

        with patch("fastapi_redis_session.session.get_version", side_effect=Exception("Version not found")):
            # Temporarily add our mock redis module
            original_redis = sys.modules.get("redis")
            sys.modules["redis"] = mock_redis_module

            try:
                SessionStorage._add_driver_info(mock_redis)

                # Should use "unknown" as version
                assert "driver_info" in mock_pool.connection_kwargs

                # Verify add_upstream_driver was called with "unknown" version
                mock_driver_info_instance.add_upstream_driver.assert_called_once_with(
                    "fastapi-redis-session", "unknown"
                )
            finally:
                # Restore original redis module
                if original_redis:
                    sys.modules["redis"] = original_redis
                else:
                    sys.modules.pop("redis", None)

    def test_add_driver_info_fallback_no_redis_version(self):
        """Test _add_driver_info fallback when redis version cannot be determined."""
        mock_redis = MagicMock()
        mock_pool = MagicMock()
        mock_pool.connection_kwargs = {}
        mock_redis.connection_pool = mock_pool

        # Create a mock redis module WITHOUT DriverInfo and WITHOUT __version__
        mock_redis_module = MagicMock(spec=[])

        with patch("fastapi_redis_session.session.get_version", return_value="0.2.0"):
            # Temporarily replace redis module
            original_redis = sys.modules.get("redis")
            sys.modules["redis"] = mock_redis_module

            try:
                SessionStorage._add_driver_info(mock_redis)

                # Should fall back to lib_name and lib_version with "unknown" for redis version
                assert "driver_info" not in mock_pool.connection_kwargs
                assert mock_pool.connection_kwargs["lib_name"] == "redis-py(fastapi-redis-session_v0.2.0)"
                assert mock_pool.connection_kwargs["lib_version"] == "unknown"
            finally:
                # Restore original redis module
                if original_redis:
                    sys.modules["redis"] = original_redis
                else:
                    sys.modules.pop("redis", None)

    def test_init_calls_add_driver_info(self):
        """Test that SessionStorage.__init__ calls _add_driver_info."""
        with patch("fastapi_redis_session.session.Redis.from_url") as mock_from_url:
            mock_redis = MagicMock()
            mock_from_url.return_value = mock_redis

            with patch.object(SessionStorage, "_add_driver_info") as mock_add_driver_info:
                SessionStorage()

                # Verify _add_driver_info was called with the redis instance
                mock_add_driver_info.assert_called_once_with(mock_redis)
