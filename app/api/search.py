import json
from datetime import date

from elasticsearch import Elasticsearch, exceptions as es_exceptions
from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies import get_db, get_redis
from ..schemas import ChatMessagesResponse, PaginationParams, PaginatedChatMessagesResponse
from ..services.chat_queries import exact_search_by_keyword, \
    paginated_exact_search_by_keyword, paginated_context_search_by_keyword, paginated_search_by_date_range
from ..services.elasticsearch_chat_queries import paginated_es_search_by_date_range, \
    paginated_es_search_by_keyword
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/api/chats/search", response_model=PaginatedChatMessagesResponse)
async def exact_search_keyword(
    search_term: str = Query(..., min_length=1, max_length=100),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Performs an exact keyword search with pagination, uses Redis for caching the results."""
    redis = await get_redis()
    if not search_term:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Generate a unique cache key for the current query and pagination settings
    cache_key = f"exact_search_keyword:{search_term}:page:{pagination.page}:size:{pagination.page_size}"
    try:
        # Attempt to get cached results from Redis
        cached_data = await redis.get(cache_key)
        if cached_data:
            # Deserialize cached data if present
            messages = PaginatedChatMessagesResponse.parse_raw(cached_data)
            if messages.count == 0:
                raise HTTPException(status_code=200, detail="No messages found")
            return messages
    except Exception as e:
        print(f"Failed to retrieve or deserialize cache: {e}")

    try:
        # Fetch results from the database if no valid cache is found
        messages = await paginated_exact_search_by_keyword(search_term, pagination, db)
        if messages.count == 0:
            raise HTTPException(status_code=200, detail="No messages found")

        # Cache the serialized response for 1 hour
        serialized_data = messages.json()
        await redis.setex(cache_key, 3600, serialized_data)
        return messages
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"An error occurred during database access or processing: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.get("/api/chats/search/all", response_model=ChatMessagesResponse)
async def exact_search_keyword_all(
    search_term: str = Query(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db)
):
    """Searches for chat messages across all data sources based on a keyword without pagination."""
    redis = await get_redis()
    if not search_term:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Key for caching all message results for a search term
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
                print(f"Error parsing cached data: {e}")
    except Exception as e:
        print(f"Redis operation failed: {e}")

    try:
        # Retrieve messages from database if cache miss or failure
        messages: ChatMessagesResponse = await exact_search_by_keyword(search_term, db)
        if messages.count == 0:
            raise HTTPException(status_code=200, detail="No messages found")

        # Serialize and set the cache for 1 hour
        serialized_data = messages.json()
        await redis.setex(cache_key, 3600, serialized_data)
        return messages
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/chats/context-search", response_model=PaginatedChatMessagesResponse)
async def search_keyword_context(
    search_term: str = Query(..., min_length=1, max_length=100),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Performs a context-based search for chat messages, with caching of the results."""
    redis = await get_redis()
    if not search_term:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Define a cache key including search term and pagination
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
    except Exception as redis_error:
        print(f"Redis operation failed: {redis_error}")

    try:
        # Retrieve messages from database, handle cache miss
        messages = await paginated_context_search_by_keyword(search_term, pagination, db)
        if messages.count == 0:
            raise HTTPException(status_code=404, detail="No messages found")

        # Serialize and cache the successful query results for 1 hour
        serialized_data = messages.json()
        await redis.setex(cache_key, 3600, serialized_data)
        return messages
    except HTTPException as he:
        raise he
    except Exception as db_error:
        print(f"Database operation failed: {db_error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/chats/search/by-date", response_model=PaginatedChatMessagesResponse)
async def search_by_date(
    start_date: date,
    end_date: date,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Searches chat messages within a specified date range with pagination and caching."""
    redis = await get_redis()
    try:
        # Construct a cache key that includes the date range and pagination parameters
        cache_key = f"search_date_range:{start_date}-{end_date}:page:{pagination.page}:size:{pagination.page_size}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            messages = PaginatedChatMessagesResponse.parse_raw(cached_data)
            if messages.count == 0:
                raise HTTPException(status_code=200, detail="No messages found")
            return messages

        # If no cache, perform a database search
        messages = await paginated_search_by_date_range(start_date, end_date, pagination, db)
        if messages.count == 0:
            raise HTTPException(status_code=200, detail="No messages found")

        # Cache the results for 1 hour after successful retrieval and serialization
        serialized_data = messages.json()
        await redis.setex(cache_key, 3600, serialized_data)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Instantiate an Elasticsearch client
es = Elasticsearch("http://localhost:9200")

@router.get("/api/es/chats/search")
async def search_keyword_in_elasticsearch(
    keyword: str,
    pagination: PaginationParams = Depends()
):
    """Searches for chat messages in Elasticsearch with keyword and pagination, includes caching."""
    redis = await get_redis()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")

    # Define a cache key with keyword and pagination details
    cache_key = f"exact_search_keyword_elasticsearch:{keyword}:page:{pagination.page}:size:{pagination.page_size}"
    try:
        cached_data = await redis.get(cache_key)
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from cache: {e}")
    except Exception as e:
        print(f"Failed to retrieve data from Redis: {e}")

    try:
        # Perform the search using Elasticsearch, handle if no results found
        messages, total = await paginated_es_search_by_keyword(keyword, pagination, es)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")

        # Build response with the search results
        response = {
            "data": messages,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.size
        }

        # Cache the serialized response for 1 hour
        await redis.setex(cache_key, 3600, json.dumps(response))
        return response
    except Exception as e:
        print(f"Error during Elasticsearch query or processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/es/chats/search/by-date")
async def search_by_date_in_elasticsearch(
    start_date: date,
    end_date: date,
    pagination: PaginationParams = Depends()
):
    """Searches for chat messages in Elasticsearch by date range, with caching of results."""
    redis = await get_redis()
    try:
        # Update cache key with date range and pagination details
        cache_key = f"elasticsearch_date_range:{start_date}-{end_date}:page:{pagination.page}:size:{pagination.page_size}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            return {"data": json.loads(cached_data), "source": "cache"}

        # If no cache, perform a search on Elasticsearch
        messages, total = await paginated_es_search_by_date_range(start_date, end_date, pagination, es)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")

        # Build the response with search results
        response = {
            "data": messages,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size
        }

        # Serialize and cache the response for 1 hour
        await redis.setex(cache_key, 3600, json.dumps(response))
        return response
    except es_exceptions.NotFoundError:
        raise HTTPException(status_code=404, detail="No messages found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
