from typing import List

from pydantic import BaseModel, Field, conint

from datetime import date


class ChatMessageCreate(BaseModel):
    message_id: str
    channel_id: str
    content: str
    timestamp: date


class ChatMessageDisplay(BaseModel):
    message_id: int
    channel_id: int
    content: str
    message_date: date

    class Config:
        orm_mode = True
        from_attributes = True
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')
        }


class ChatMessagesResponse(BaseModel):
    messages: List[ChatMessageDisplay]
    count: int


class PaginatedChatMessagesResponse(BaseModel):
    messages: List[ChatMessageDisplay]
    count: int
    total_count: int


class PaginationParams(BaseModel):
    page: int = Field(default=1, gt=0, description="The page number starting from 1")
    page_size: int = Field(default=10, gt=0, le=100, description="The number of items per page, max 100")

    def skip(self):
        """Calculate the number of records to skip for the database query based on the current page and page size."""
        return (self.page - 1) * self.page_size
