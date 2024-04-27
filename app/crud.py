from sqlalchemy.orm import Session
from . import models, schemas

def create_chat_message(db: Session, chat_message: schemas.ChatMessageCreate):
    db_message = models.ChatMessage(**chat_message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
