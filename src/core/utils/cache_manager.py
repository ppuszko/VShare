from redis.asyncio import Redis, ConnectionPool
from fastapi import Request, Depends

from src.core.config.db import DBConfig


def init_redis() -> Redis:
    pool = ConnectionPool.from_url(DBConfig.REDIS_URL, decode_responses=True)
    return Redis(connection_pool=pool)

def get_redis(request: Request) -> Redis:
    return request.app.state.redis

def get_cache_manager(r: Redis = Depends(get_redis)):
    return CacheManager(r)

class CacheManager:
    def __init__(self, redis: Redis):
        self._redis: Redis = redis


    async def insert_ticket(self, ticket: str, expiry_seconds: int = 1200):
        await self._redis.set(f"ticket:{ticket}", 0, ex=expiry_seconds)


    async def should_process_ticket(self, ticket: str) -> bool:
        val = await self._redis.get(f"ticket:{ticket}")

        if val == "0":
            await self._redis.set(f"ticket:{ticket}", 1, keepttl=True)
            return True
        return False
    

    async def get_cached_categories(self, group_uid: str) -> dict:
        categories = await self._redis.hgetall(f"categories:{group_uid}") # type: ignore[reportGeneralTypeIssues]
        return categories
    
    async def set_cached_categories(self, group_uid: str, categories: dict):
        await self._redis.hset(f"categories:{group_uid}", mapping=categories) # type: ignore[reportGeneralTypeIssues]