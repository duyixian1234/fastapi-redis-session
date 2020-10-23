from fastapi_redis_session.config import basicConfig, config
import random
from unittest import mock


@mock.patch("fastapi_redis_session.config.uuid4")
def testConfig(mock_uuid4):
    config.genSessionId()
    mock_uuid4.assert_called_once_with()


def testBasicConfig():
    origin = config.settings["sessionIdGenerator"]
    basicConfig(
        redisURL="redis://localhost:6379/1",
        sessionIdName="sessionId",
        sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
    )
    assert config.redisURL == "redis://localhost:6379/1"
    assert config.sessionIdName == "sessionId"
    assert config.genSessionId().isnumeric()

    basicConfig(sessionIdGenerator=origin)
