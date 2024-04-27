from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
from ..dependencies import get_db
from ..models import Message
from ..schemas import ChatMessageDisplay
from ..services.chat_queries import search_by_keyword
from ..services.chat_queries import search_by_date_range

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/search/keyword/")
# @router.get("/search/keyword/", response_model=List[ChatMessageDisplay])
async def search_keyword(keyword: str, db: db_dependency):
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")
    messages = search_by_keyword(keyword, db)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    return messages

from datetime import date

@router.get("/search/date/")
async def search_by_date(start_date: date, end_date: date, db: db_dependency):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    messages = search_by_date_range(start_date, end_date, db)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    return messages

