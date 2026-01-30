from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis | None

async def init_redis() -> None:
    global redis_client
    
    if not redis_client:
        redis_client = Redis.from_url(
            url=settings.REDIS_URI,
            decode_response=True
        )
        
async def close_redis() -> None:
    if redis_client:
        await redis_client.close()
        
async def get_redis() -> Redis:
    if not redis_client:
        raise RuntimeError("Redis is not initiallized")
    
    return redis_client