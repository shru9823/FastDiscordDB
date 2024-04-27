from pydantic import BaseModel
from datetime import date

class ChatMessageCreate(BaseModel):
    message_id: str
    channel_id: str
    content: str
    timestamp: date

class ChatMessageDisplay(BaseModel):
    message_id: str
    content: str
    timestamp: date

    class Config:
        orm_mode = True
