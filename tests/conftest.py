from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from database.utils import get_db
from main import app


# mock redis
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """
    Replaces Redis with FakeRedis.
    """
    fake_r = fakeredis.aioredis.FakeRedis(decode_responses=True)

    def get_fake_redis(*args, **kwargs):
        return fake_r

    monkeypatch.setattr("redis.asyncio.from_url", get_fake_redis)
    return fake_r


# mock db session
async def override_get_db():
    """
    Fake session for endpoints.
    Replace Depends(get_db).
    """
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.scalars = MagicMock()
    yield mock_session


# client fixtures
@pytest.fixture(scope="session")
def client():
    # replace session dependency for db
    app.dependency_overrides[get_db] = override_get_db

    # create mock plug
    mock_init = AsyncMock(return_value=None)

    # patch main.init_db not a database.base.init_db
    with patch("main.init_db", side_effect=mock_init):
        # make Sentry silenced
        with patch("logs.sentry.init_sentry", return_value=None):
            # create client
            with TestClient(app) as c:
                yield c

    app.dependency_overrides = {}
