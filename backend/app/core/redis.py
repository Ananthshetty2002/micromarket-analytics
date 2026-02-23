requirement\backend\app\core\redis.py
```

```python
"""
Redis client configuration for caching and pub/sub
"""
import redis.asyncio as redis
from typing import Optional
import os

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Global redis client instance
redis_client: Optional[redis.Redis] = None


async def init_redis() -> redis.Redis:
    """Initialize Redis connection"""
    global redis_client
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30
    )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        await init_redis()
    return redis_client


class RedisCache:
    """Helper class for Redis caching operations"""

    @staticmethod
    async def get(key: str) -> Optional[str]:
        """Get value from cache"""
        client = await get_redis()
        return await client.get(key)

    @staticmethod
    async def set(key: str, value: str, expire: int = 300):
        """Set value in cache with expiration (seconds)"""
        client = await get_redis()
        await client.setex(key, expire, value)

    @staticmethod
    async def setex(key: str, seconds: int, value: str):
        """Set value with expiration"""
        client = await get_redis()
        await client.setex(key, seconds, value)

    @staticmethod
    async def delete(key: str):
        """Delete key from cache"""
        client = await get_redis()
        await client.delete(key)

    @staticmethod
    async def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)

    @staticmethod
    async def flush():
        """Flush all cache (use with caution)"""
        client = await get_redis()
        await client.flushdb()


# Convenience functions for direct import
async def cache_get(key: str) -> Optional[str]:
    return await RedisCache.get(key)


async def cache_set(key: str, value: str, expire: int = 300):
    return await RedisCache.set(key, value, expire)


async def cache_delete(key: str):
    return await RedisCache.delete(key)
