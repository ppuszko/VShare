import redis.asyncio as redis
from fastapi import Request, Depends

from src.core.config.db import DBConfig

def init_redis() -> redis.Redis:
    pool = redis.ConnectionPool.from_url(DBConfig.REDIS_URL, decode_responses=True)
    return redis.Redis(connection_pool=pool)

def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis

def get_cache_manager(r: redis.Redis = Depends(get_redis)):
    return CacheManager(r)

class CacheManager:
    def __init__(self, redis: redis.Redis):
        self._redis = redis


    async def insert_ticket(self, ticket: str, expiry_seconds: int = 1200):
        await self._redis.set(f"ticket:{ticket}", 0, ex=expiry_seconds)

    async def should_process_ticket(self, ticket: str) -> bool:
        val = await self._redis.get(f"ticket:{ticket}")
        if val == 0:
            await self._redis.set(f"ticket:{ticket}", 1, keepttl=True)
            return True
        return False
    
    async def get_cached_categories(self, group_uid: str):
        categories = await self._redis.hgetall(f"categories:{group_uid}") # type: ignore