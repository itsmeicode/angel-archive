import json
from typing import Optional, Callable
from functools import wraps

from app.config.redis import get_redis

DEFAULT_EXPIRATION = 3600  # 1 hour


async def get_cached(key: str) -> Optional[str]:
    """Get value from cache"""
    redis_client = await get_redis()
    if not redis_client:
        return None
    
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


async def set_cached(key: str, value: str, expiration: int = DEFAULT_EXPIRATION):
    """Set value in cache with expiration"""
    redis_client = await get_redis()
    if not redis_client:
        return
    
    try:
        await redis_client.setex(key, expiration, value)
    except Exception as e:
        print(f"Cache set error: {e}")


async def invalidate_cache(pattern: str):
    """Invalidate cache keys matching pattern"""
    redis_client = await get_redis()
    if not redis_client:
        return
    
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            print(f"Invalidated {len(keys)} cache keys matching: {pattern}")
    except Exception as e:
        print(f"Cache invalidation error: {e}")


async def get_cache_stats() -> dict:
    """Get cache connection stats"""
    redis_client = await get_redis()
    
    if not redis_client:
        return {
            "connected": False,
            "error": "Redis not connected",
        }
    
    try:
        info = await redis_client.info("stats")
        return {
            "connected": True,
            "info": info,
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }
