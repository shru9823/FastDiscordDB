import time
import logging
from fastapi.responses import JSONResponse
from starlette import status
from ..dependencies import get_db, get_redis
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from ..services import chat_exporter, elasticsearch_chat_exporter
from pyinstrument import Profiler
from ..settings import get_settings
from aiofiles import open as aio_open  # For asynchronous file operations

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

async def clear_redis_cache(redis):
    """Clear the entire Redis cache."""
    await redis.flushdb()

# Dependency to validate and retrieve the Discord token from the header
async def get_discord_token(x_token: str = Header(...)):
    """Retrieve the Discord token from headers, raising an error if it is missing."""
    if x_token is None:
        raise HTTPException(status_code=400, detail="Missing Discord token.")
    return x_token

@router.post("/api/chats/export/{channel_id}", status_code=status.HTTP_200_OK)
async def export_chat_to_postgres(channel_id: str, discord_token: str = Depends(get_discord_token), db: AsyncSession = Depends(get_db)):
    """API endpoint to export chat data to a Postgres database."""
    settings = get_settings()  # Load application settings
    redis = await get_redis()  # Get a Redis connection
    try:
        if settings.profiling:
            profiler = Profiler(interval=settings.profile_interval, async_mode="enabled")
            profiler.start()
        start_time = time.time()  # Start timing the operation

        response = await chat_exporter.export_chat(discord_token, channel_id, db)

        process_time = time.time() - start_time  # Calculate processing time

        # Record the export operation in Redis
        await redis.set("last_export_time", int(time.time()))
        await clear_redis_cache(redis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if settings.profiling:
            profiler.stop()
            html_output = profiler.output_html()  # Get the HTML output from profiler
            async with aio_open(f'profiling_results_{channel_id}.html', 'w') as file:
                await file.write(html_output)  # Write the HTML output to a local file
            logger.info(f"export_chat processed in {process_time:.4f} seconds; profiling saved to 'profiling_results_{channel_id}.html'")
    return JSONResponse(status_code=200, content={
        "status": "success",
        "data": response,
        "process_time": f"{process_time:.4f} seconds"
    })

@router.post("/api/es/chats/export/{channel_id}", status_code=status.HTTP_200_OK)
async def export_chat_to_elasticsearch(channel_id: str, discord_token: str = Depends(get_discord_token)):
    """API endpoint to export chat data to Elasticsearch."""
    settings = get_settings()  # Load application settings
    redis = await get_redis()  # Get a Redis connection
    try:
        if settings.profiling:
            profiler = Profiler(interval=settings.profile_interval, async_mode="enabled")
            profiler.start()
        start_time = time.time()  # Start timing the operation

        response = await elasticsearch_chat_exporter.export_chat(discord_token, channel_id)

        process_time = time.time() - start_time  # Calculate processing time

        # Record the export operation in Redis
        await redis.set("last_export_time_elastic", int(time.time()))
        await clear_redis_cache(redis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if settings.profiling:
            profiler.stop()
            html_output = profiler.output_html()  # Get the HTML output from profiler
            async with aio_open(f'profiling_results_elastic_{channel_id}.html', 'w') as file:
                await file.write(html_output)  # Write the HTML output to a local file
            logger.info(f"export_chat to Elasticsearch processed in {process_time:.4f} seconds; profiling saved to 'profiling_results_elastic_{channel_id}.html'")
    return JSONResponse(status_code=200, content={
        "status": "success",
        "data": response,
        "process_time": f"{process_time:.4f} seconds"
    })
