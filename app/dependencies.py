# Assuming `async_session` is an AsyncSession factory
from .core.database import async_session
import aioredis


async def get_db():
    async with async_session() as session:
        async with session.begin():
            yield session

# Configure global connection (usually better to use dependency injection)
redis = None


async def startup_redis():
    global redis
    redis = aioredis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True
    )


async def shutdown_redis():
    global redis
    await redis.close()
    # await redis.wait_closed()


async def get_redis():
    if redis is None:
        await startup_redis()
    return redis