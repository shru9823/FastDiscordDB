import json
import time
from datetime import date

from elasticsearch import Elasticsearch, exceptions as es_exceptions
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import parse_obj_as
from sqlalchemy.orm import Session
from typing import List, Annotated
from ..dependencies import get_db, get_redis
from ..models import Message
from ..schemas import ChatMessageDisplay, ChatMessagesResponse, PaginationParams, PaginatedChatMessagesResponse
from ..services.chat_queries import exact_search_by_keyword, \
    paginated_exact_search_by_keyword, paginated_context_search_by_keyword, paginated_search_by_date_range
from ..services.elasticsearch_chat_queries import paginated_es_search_by_date_range, \
    paginated_es_search_by_keyword
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# # Using AsyncSession for async database operations
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.get("/api/chats/search", response_model=PaginatedChatMessagesResponse)
async def exact_search_keyword(
    search_term: str = Query(..., min_length=1, max_length=100),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    redis = await get_redis()
    if not search_term:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Include pagination parameters in the cache key
    cache_key = f"exact_search_keyword:{search_term}:page:{pagination.page}:size:{pagination.page_size}"
    try:
        # Attempt to retrieve cached data
        cached_data = await redis.get(cache_key)
        if cached_data:
            # Deserialize and return if cache is valid
            messages = PaginatedChatMessagesResponse.parse_raw(cached_data)
            if messages.count == 0:
                raise HTTPException(status_code=200, detail="No messages found")
            return messages
    except Exception as e:
        # Log cache retrieval or deserialization errors and continue
        print(f"Failed to retrieve or deserialize cache: {e}")
    try:
        # Perform the database search if cache miss or failure
        messages = await paginated_exact_search_by_keyword(search_term, pagination, db)
        if messages.count == 0:
            raise HTTPException(status_code=200, detail="No messages found")

        # Serialize and set the cache
        serialized_data = messages.json()
        await redis.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour
        return messages
    except HTTPException as http_exc:
        # Specific catch for HTTPException to reraise it
        raise http_exc
    except Exception as e:
        # Catch other exceptions that could occur during DB access or processing
        print(f"An error occurred during database access or processing: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")


@router.get("/api/chats/search/all", response_model=ChatMessagesResponse)
async def exact_search_keyword(search_term: str = Query(..., min_length=1, max_length=100), db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    if not search_term:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    cache_key = f"exact_search_keyword_all:{search_term}"
    try:
        cached_data = await redis.get(cache_key)
        if cached_data:
            try:
                messages = ChatMessagesResponse.parse_raw(cached_data)
                if messages.count == 0:
                    raise HTTPException(status_code=404, detail="No messages found")
                return messages
            except Exception as e:
                # Log error and continue to fetch from DB if cache parsing fails
                print(f"Error parsing cached data: {e}")
    except Exception as e:
        print(f"Redis operation failed: {e}")  # Logging Redis errors

    try:
        messages: ChatMessagesResponse = await exact_search_by_keyword(search_term, db)
        if messages.count == 0:
            raise HTTPException(status_code=200, detail="No messages found")

        # Serialize and set the cache
        try:
            serialized_data = messages.json()
            await redis.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour
        except Exception as e:
            print(f"Error serializing or setting cache: {e}")

        return messages
    except HTTPException as he:
        # Re-raise HTTPException to keep status code and detail intact
        raise he
    except Exception as e:
        print(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/chats/context-search", response_model=PaginatedChatMessagesResponse)
async def search_keyword(
    search_term: str = Query(..., min_length=1, max_length=100),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    redis = await get_redis()
    if not search_term:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Include pagination parameters in the cache key
    cache_key = f"context_search_keyword:{search_term}:page:{pagination.page}:size:{pagination.page_size}"

    try:
        cached_data = await redis.get(cache_key)
        if cached_data:
            try:
                messages = PaginatedChatMessagesResponse.parse_raw(cached_data)
                if messages.count == 0:
                    raise HTTPException(status_code=200, detail="No messages found")
                return messages
            except Exception as parse_error:
                print(f"Failed to parse cached data: {parse_error}")
                # Continue to fetch from DB if parsing fails
    except Exception as redis_error:
        print(f"Redis operation failed: {redis_error}")
        # Continue to database if Redis fails

    try:
        messages = await paginated_context_search_by_keyword(search_term, pagination, db)
        if messages.count == 0:
            raise HTTPException(status_code=404, detail="No messages found")

        try:
            # Serialize and set the cache
            serialized_data = messages.json()
            await redis.setex(cache_key, 3600, serialized_data)
        except Exception as cache_set_error:
            print(f"Error serializing or setting cache: {cache_set_error}")
        return messages
    except HTTPException as he:
        # Reraise the HTTPException to preserve specific status codes and details
        raise he
    except Exception as db_error:
        print(f"Database operation failed: {db_error}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/api/chats/search/by-date", response_model=PaginatedChatMessagesResponse)
async def search_by_date(start_date: date,
                         end_date: date,
                         pagination: PaginationParams = Depends(),
                         db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    try:
        # Update cache key to include pagination parameters
        cache_key = f"search_date_range:{start_date}-{end_date}:page:{pagination.page}:size:{pagination.page_size}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            messages = PaginatedChatMessagesResponse.parse_raw(cached_data)
            if messages.count == 0:
                raise HTTPException(status_code=200, detail="No messages found")
            return messages

        messages = await paginated_search_by_date_range(start_date, end_date, pagination, db)

        if messages.count == 0:
            raise HTTPException(status_code=200, detail="No messages found")

        # Serialize and set the cache
        serialized_data = messages.json()
        await redis.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


es = Elasticsearch("http://localhost:9200")
print(es.ping())


@router.get("/api/es/chats/search")
async def search_keyword(keyword: str, pagination: PaginationParams = Depends()):
    redis = await get_redis()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Update the cache key to include pagination parameters
    cache_key = f"exact_search_keyword_elasticsearch:{keyword}:page:{pagination.page}:size:{pagination.page_size}"
    try:
        cached_data = await redis.get(cache_key)
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from cache: {e}")
                # Possible fallback or additional logging here
    except Exception as e:
        print(f"Failed to retrieve data from Redis: {e}")
        # Optional: Continue to fetch from Elasticsearch or handle the failure as needed

    try:
        messages, total = await paginated_es_search_by_keyword(keyword, pagination, es)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")

        response = {
            "data": messages,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.size
        }

        try:
            # Serialize response before caching
            await redis.setex(cache_key, 3600, json.dumps(response))
        except Exception as e:
            print(f"Failed to set cache in Redis: {e}")
            # Handling failed cache set; optional logging or fallback actions
        return response
    except Exception as e:
        print(f"Error during Elasticsearch query or processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/api/es/chats/search/by-date")
async def search_by_date(
        start_date: date,
        end_date: date,
        pagination: PaginationParams = Depends()):
    redis = await get_redis()
    try:
        # Update cache key to include pagination parameters
        cache_key = f"elasticsearch_date_range:{start_date}-{end_date}:page:{pagination.page}:size:{pagination.page_size}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            return {"data": json.loads(cached_data), "source": "cache"}

        messages, total = await paginated_es_search_by_date_range(start_date, end_date, pagination, es)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")

        response = {
            "data": messages,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size
        }

        # Serialize response before caching
        await redis.setex(cache_key, 3600, json.dumps(response))  # Cache for 1 hour
        return response
    except es_exceptions.NotFoundError:
        raise HTTPException(status_code=404, detail="No messages found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
