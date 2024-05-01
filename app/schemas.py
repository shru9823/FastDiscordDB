from typing import List
from pydantic import BaseModel, Field, conint
from datetime import date

# Define a Pydantic model for creating a new chat message
class ChatMessageCreate(BaseModel):
    message_id: str  # Unique identifier for the message as a string
    channel_id: str  # Identifier for the channel from which the message originates
    content: str  # Text content of the message
    timestamp: date  # Date when the message was sent

# Define a Pydantic model for displaying chat messages
class ChatMessageDisplay(BaseModel):
    message_id: int  # Message ID converted to integer
    channel_id: int  # Channel ID as an integer
    content: str  # Text content of the message
    message_date: date  # Date when the message was sent

    # Configuration class included in Pydantic models to provide additional settings
    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models
        from_attributes = True  # Assume model attributes can be read directly from ORM
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')  # Custom encoder for date format
        }

# Define a Pydantic model for a standard response containing a list of messages
class ChatMessagesResponse(BaseModel):
    messages: List[ChatMessageDisplay]  # List of chat messages to display
    count: int  # Number of messages in the response

# Define a Pydantic model for paginated responses of chat messages
class PaginatedChatMessagesResponse(BaseModel):
    messages: List[ChatMessageDisplay]  # List of chat messages
    count: int  # Number of messages in the current page
    total_count: int  # Total number of messages available across all pages

# Define a Pydantic model for pagination parameters
class PaginationParams(BaseModel):
    page: int = Field(default=1, gt=0, description="The page number starting from 1")  # Current page number, must be greater than 0
    page_size: int = Field(default=10, gt=0, le=100, description="The number of items per page, max 100")  # Number of items per page with a maximum of 100

    def skip(self):
        """Calculate the number of records to skip for the database query based on the current page and page size."""
        return (self.page - 1) * self.page_size  # Derived attribute to calculate offset for pagination
