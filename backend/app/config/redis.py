import redis.asyncio as redis
from typing import Optional

from app.config.settings import get_settings

settings = get_settings()

redis_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client connection"""
    global redis_client
    
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return None
    
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
