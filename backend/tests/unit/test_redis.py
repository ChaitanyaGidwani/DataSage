"""Unit tests for Redis cache utilities and offline resilience."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from datasage.core.redis import (
    cache_delete,
    cache_get,
    cache_get_json,
    cache_set,
    cache_set_json,
    close_redis,
    get_redis_client,
    is_redis_available,
)


@pytest.mark.asyncio
async def test_is_redis_available_offline() -> None:
    """Test is_redis_available gracefully returns False when Redis is unreachable."""
    with patch("datasage.core.redis.get_redis_client", return_value=None):
        available = await is_redis_available()
        assert available is False


@pytest.mark.asyncio
async def test_cache_offline_fallback() -> None:
    """Test cache functions degrade gracefully when Redis client is None."""
    with patch("datasage.core.redis.get_redis_client", return_value=None):
        val = await cache_get("test_key")
        assert val is None

        set_result = await cache_set("test_key", "value")
        assert set_result is False

        del_result = await cache_delete("test_key")
        assert del_result is False

        json_val = await cache_get_json("test_key")
        assert json_val is None

        json_set_result = await cache_set_json("test_key", {"a": 1})
        assert json_set_result is False


@pytest.mark.asyncio
async def test_cache_with_mocked_client() -> None:
    """Test cache operations succeed with an active mock Redis client."""
    mock_client = AsyncMock()
    mock_client.ping.return_value = True
    mock_client.get.return_value = json.dumps({"test": 123})
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1

    with patch("datasage.core.redis.get_redis_client", return_value=mock_client):
        # Ping
        assert await is_redis_available() is True

        # JSON get
        res = await cache_get_json("dummy_key")
        assert res == {"test": 123}

        # JSON set
        ok = await cache_set_json("dummy_key", {"test": 123}, ttl=60)
        assert ok is True
        mock_client.set.assert_called_once_with("dummy_key", '{"test": 123}', ex=60)

        # Delete
        deleted = await cache_delete("dummy_key")
        assert deleted is True


@pytest.mark.asyncio
async def test_cache_close_redis() -> None:
    """Test closing Redis client connection."""
    mock_client = AsyncMock()
    with patch("datasage.core.redis._redis_client", mock_client):
        await close_redis()
        mock_client.close.assert_called_once()
