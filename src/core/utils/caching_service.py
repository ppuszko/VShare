import redis.asyncio as redis
from fastapi import Request


def init_redis() -> redis.Redis:
    pool = redis.ConnectionPool.from_url("redis://localhost", decode_responses=True)
    return redis.Redis(connection_pool=pool)

def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis

class CachingService:
    def __init__(self, r: redis.Redis):
        self.r = r


    async def insert_ticket(self, ticket: str, expiry_seconds: int = 1200):
        await self.r.set(f"ticket:{ticket}", 0, ex=expiry_seconds)

    async def should_process_ticket(self, ticket: str) -> bool:
        val = await self.r.get(f"ticket:{ticket}")
        if val == 0:
            await self.r.set(f"ticket:{ticket}", 1, keepttl=True)
            return True
        return False