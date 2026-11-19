"""Redis client and caching utilities for DataSage backend.

Provides async cache operations with automatic graceful degradation
when Redis is unavailable or offline.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError

from datasage.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


def get_redis_client() -> aioredis.Redis | None:
    """Get or initialize the global async Redis client."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = aioredis.from_url(  # type: ignore[no-untyped-call]
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
        except Exception as e:
            logger.warning("Failed to initialize Redis client: %s", e)
            return None
    return _redis_client


async def close_redis() -> None:
    """Close the global Redis client connection."""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.close()
        except Exception as e:
            logger.warning("Error closing Redis connection: %s", e)
        finally:
            _redis_client = None


async def is_redis_available() -> bool:
    """Check if Redis connection is active and responding."""
    client = get_redis_client()
    if not client:
        return False
    try:
        return bool(await client.ping())
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.debug("Redis ping failed: %s", e)
        return False
    except Exception as e:
        logger.warning("Unexpected error during Redis ping: %s", e)
        return False


async def cache_get(key: str) -> str | None:
    """Retrieve string value from Redis cache."""
    client = get_redis_client()
    if not client:
        return None
    try:
        val = await client.get(key)
        return str(val) if val is not None else None
    except (ConnectionError, TimeoutError, OSError):
        return None
    except Exception as e:
        logger.debug("Redis GET error for key %s: %s", key, e)
        return None


async def cache_set(key: str, value: str, ttl: int | None = None) -> bool:
    """Store string value in Redis cache with optional TTL."""
    client = get_redis_client()
    if not client:
        return False
    try:
        ttl = ttl or settings.REDIS_CACHE_TTL_SECONDS
        await client.set(key, value, ex=ttl)
        return True
    except (ConnectionError, TimeoutError, OSError):
        return False
    except Exception as e:
        logger.debug("Redis SET error for key %s: %s", key, e)
        return False


async def cache_get_json(key: str) -> dict[str, Any] | list[Any] | None:
    """Retrieve JSON-deserialized object from Redis cache."""
    data = await cache_get(key)
    if data:
        try:
            parsed: object = json.loads(data)
            if isinstance(parsed, (dict, list)):
                return parsed
            return None
        except json.JSONDecodeError:
            return None
    return None


async def cache_set_json(key: str, value: Any, ttl: int | None = None) -> bool:
    """Serialize and store JSON-compatible object in Redis cache."""
    try:
        serialized = json.dumps(value, default=str)
        return await cache_set(key, serialized, ttl=ttl)
    except (TypeError, ValueError) as e:
        logger.debug("Failed to JSON-serialize cache payload for key %s: %s", key, e)
        return False


async def cache_delete(key: str) -> bool:
    """Remove key from Redis cache."""
    client = get_redis_client()
    if not client:
        return False
    try:
        await client.delete(key)
        return True
    except (ConnectionError, TimeoutError, OSError):
        return False
    except Exception as e:
        logger.debug("Redis DELETE error for key %s: %s", key, e)
        return False
