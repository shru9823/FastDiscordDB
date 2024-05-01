import time
from fastapi.responses import JSONResponse
from starlette import status
from ..dependencies import get_db, get_redis
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from ..services import chat_exporter, elasticsearch_chat_exporter
from pyinstrument import Profiler

from ..settings import get_settings

router = APIRouter()


async def clear_redis_cache(redis):
    # This will clear the entire Redis cache
    await redis.flushdb()


# Dependency to validate and retrieve the Discord token from the header
async def get_discord_token(x_token: str = Header(...)):
    if x_token is None:
        raise HTTPException(status_code=400, detail="Missing Discord token.")
    return x_token


@router.post("/api/chats/export/{channel_id}", status_code=status.HTTP_200_OK)
async def export_chat_to_postgres(channel_id: str, discord_token: str = Depends(get_discord_token), db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    redis = await get_redis()
    try:
        if settings.profiling:
            profiler = Profiler(interval=settings.profile_interval,
                                async_mode="enabled")
            profiler.start()
        start_time = time.time()  # Start timing

        response = await chat_exporter.export_chat(discord_token, channel_id, db)

        process_time = time.time() - start_time  # End timing

        # Mark the export operation in Redis
        await redis.set("last_export_time", int(time.time()))
        await clear_redis_cache(redis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if settings.profiling:
            profiler.stop()
            print(profiler.output_html())
            print(f"export_chat processed in {process_time:.4f} seconds")
    # Successful response with status code 200
    return JSONResponse(status_code=200, content={
        "status": "success",
        "data": response,
        "process_time": f"{process_time:.4f} seconds"
    })


@router.post("/api/es/chats/export/{channel_id}", status_code=status.HTTP_200_OK)
async def export_chat_to_elasticsearch(channel_id: str, discord_token: str = Depends(get_discord_token)):
    settings = get_settings()
    redis = await get_redis()
    try:
        if settings.profiling:
            profiler = Profiler(interval=settings.profile_interval,
                                async_mode="enabled")
            profiler.start()
        start_time = time.time()  # Start timing

        response = await elasticsearch_chat_exporter.export_chat(discord_token, channel_id)

        process_time = time.time() - start_time  # End timing

        # Mark the export operation in Redis
        await redis.set("last_export_time_elastic", int(time.time()))
        await clear_redis_cache(redis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if settings.profiling:
            profiler.stop()
            print(profiler.output_html())
            print(f"export_chat processed in {process_time:.4f} seconds")
    # Successful response with status code 200
    return JSONResponse(status_code=200, content={
        "status": "success",
        "data": response,
        "process_time": f"{process_time:.4f} seconds"
    })
