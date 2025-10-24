"""Redis connection and distributed lock helpers."""

from __future__ import annotations

import time
from typing import Optional

import redis

from core.settings import settings

_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """Get or create a Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
    return _redis_client


def acquire_lock(key: str, ttl_seconds: int) -> bool:
    """Attempt to acquire a distributed lock.

    Returns True if lock acquired, False otherwise.
    """
    client = get_redis()
    return client.set(name=key, value=str(time.time()), nx=True, ex=ttl_seconds) is True


def release_lock(key: str) -> None:
    """Release a distributed lock by key."""
    client = get_redis()
    client.delete(key)
