import logging
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.exceptions import HTTPException

# Importing models and schemas necessary for operations
from ..models import Message, Base
from ..schemas import ChatMessageDisplay, ChatMessagesResponse, PaginationParams, PaginatedChatMessagesResponse

# Setting up logging to monitor and log the application's actions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def paginated_exact_search_by_keyword(search_term: str, pagination: PaginationParams, session: AsyncSession):
    """
    Performs a paginated search by a given keyword in the database.
    It utilizes full-text search capabilities and logs detailed information.
    """
    try:
        # Prepare a query for full-text search
        query = func.plainto_tsquery('english', search_term)
        # SQL statement that filters messages containing the search term, with pagination
        stmt = select(Message).filter(
            Message.content.ilike(f"%{search_term}%")
        ).offset(pagination.skip()).limit(pagination.page_size)

        # Execute the SQL statement
        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")

        # Additional SQL to count total results for pagination
        total_count_stmt = select(func.count()).select_from(Message).filter(
            Message.content.ilike(f"%{search_term}%")
        )
        total_count_result = await session.execute(total_count_stmt)
        total_count = total_count_result.scalar_one()

        return PaginatedChatMessagesResponse(messages=[ChatMessageDisplay.from_orm(msg) for msg in messages], count=len(messages), total_count=total_count)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request.")

async def exact_search_by_keyword(search_term: str, session: AsyncSession):
    """
    Performs a non-paginated search for messages containing the exact search term using full-text search capabilities.
    """
    try:
        query = func.plainto_tsquery('english', search_term)
        # Combining full-text search with a like filter for precise matching
        stmt = select(Message).filter(
            Message.content_tsvector.op('@@')(query),
            Message.content.ilike(f"%{search_term}%")
        )
        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")
        return ChatMessagesResponse(messages=[ChatMessageDisplay.from_orm(msg) for msg in messages], count=len(messages))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request.")

async def paginated_context_search_by_keyword(search_term: str, pagination: PaginationParams, session: AsyncSession):
    """
    Performs a paginated full-text search for messages relevant to the context defined by the search term.
    """
    try:
        query = func.plainto_tsquery('english', search_term)
        # Contextual search across messages using the tsvector column
        stmt = select(Message).filter(
            Message.content_tsvector.op('@@')(query)
        ).offset(pagination.skip()).limit(pagination.page_size)

        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")

        # Counting total messages for pagination
        total_count_stmt = select(func.count()).select_from(Message).filter(
            Message.content_tsvector.op('@@')(query)
        )
        total_count_result = await session.execute(total_count_stmt)
        total_count = total_count_result.scalar_one()

        return PaginatedChatMessagesResponse(messages=[ChatMessageDisplay.from_orm(msg) for msg in messages], count=len(messages), total_count=total_count)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request.")

async def paginated_search_by_date_range(start_date: date, end_date: date, pagination: PaginationParams, session: AsyncSession):
    """
    Searches for messages within a specified date range with pagination.
    Fetches and counts messages to facilitate client-side pagination.
    """
    try:
        # SQL statement that retrieves messages within the date range with pagination
        stmt = select(Message).filter(
            Message.message_date.between(start_date, end_date)
        ).offset(pagination.skip()).limit(pagination.page_size)

        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")

        # Count total messages within the date range
        total_count_stmt = select(func.count()).select_from(Message).filter(
            Message.message_date.between(start_date, end_date)
        )
        total_count_result = await session.execute(total_count_stmt)
        total_count = total_count_result.scalar_one()

        return PaginatedChatMessagesResponse(messages=[ChatMessageDisplay.from_orm(msg) for msg in messages], count=len(messages), total_count=total_count)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request.")
