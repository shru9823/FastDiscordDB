import logging
import subprocess
from datetime import datetime, timedelta, date

import json
from datetime import datetime
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.exceptions import HTTPException

# Assuming you've defined models corresponding to your table
from ..models import Message, Base
from ..schemas import ChatMessageDisplay, ChatMessagesResponse, PaginationParams, PaginatedChatMessagesResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def paginated_exact_search_by_keyword(search_term: str, pagination: PaginationParams, session: AsyncSession):
    try:
        query = func.plainto_tsquery('english', search_term)
        stmt = select(Message).filter(
            Message.content.ilike(f"%{search_term}%")
        ).offset(pagination.skip()).limit(pagination.page_size)

        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")

        # Get total count for pagination
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
    try:
        query = func.plainto_tsquery('english', search_term)
        # Perform the query using both the full-text search and exact match criteria
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
    try:
        query = func.plainto_tsquery('english', search_term)
        stmt = select(Message).filter(
            Message.content_tsvector.op('@@')(query)
        ).offset(pagination.skip()).limit(pagination.page_size)

        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")

        # Get total count for pagination
        total_count_stmt = select(func.count()).select_from(Message).filter(
            Message.content.ilike(f"%{search_term}%")
        )
        total_count_result = await session.execute(total_count_stmt)
        total_count = total_count_result.scalar_one()

        return PaginatedChatMessagesResponse(messages=[ChatMessageDisplay.from_orm(msg) for msg in messages],
                                             count=len(messages), total_count=total_count)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request.")


async def paginated_search_by_date_range(start_date: date, end_date: date, pagination: PaginationParams, session: AsyncSession):
    try:
        # stmt = select(Message).filter(Message.message_date.between(start_date, end_date))
        stmt = select(Message).filter(Message.message_date.between(
            start_date, end_date)).offset(pagination.skip()).limit(pagination.page_size)

        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")

        # Get total count for pagination
        total_count_stmt = select(func.count()).select_from(Message).filter(
            Message.message_date.between(start_date, end_date))
        total_count_result = await session.execute(total_count_stmt)
        total_count = total_count_result.scalar_one()

        return PaginatedChatMessagesResponse(messages=[ChatMessageDisplay.from_orm(msg) for msg in messages],
                                             count=len(messages), total_count=total_count)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request.")

        result = await session.execute(stmt)
        messages = result.scalars().all()
        logger.info(f"Successfully fetched {len(messages)} messages from the database.")
        return [ChatMessageDisplay.from_orm(msg) for msg in messages]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e

# try:
    #     query = func.plainto_tsquery('english', search_term)
    #     stmt = select(Message).filter(Message.content_tsvector.op('@@')(query))
    #     result = await session.execute(stmt)
    #     messages = result.scalars().all()
    #     logger.info(f"Successfully fetched {len(messages)} messages from the database.")
    #     return [ChatMessageDisplay.from_orm(msg) for msg in messages]
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    #     raise e