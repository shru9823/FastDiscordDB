from typing import Annotated

from ..dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services import chat_exporter

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/export/{channel_id}")
async def export_chat(token: str, channel_id: str, db: db_dependency):
    try:
        chat_exporter.export_chat(token, channel_id, db)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
