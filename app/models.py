from sqlalchemy import Column, String, DateTime, ForeignKey, Date, BIGINT
from sqlalchemy.dialects.postgresql import TSVECTOR
from .core.database import Base


class Message(Base):
    __tablename__ = 'discord_chats'

    # Discord specific fields
    message_id = Column(BIGINT, primary_key=True, index=True,
                        nullable=False)  # Unique Discord message ID
    channel_id = Column(BIGINT, nullable=False)  # Discord channel ID
    content = Column(String)  # Content of the message
    message_date = Column(Date, nullable=False)  # Date of when the message was sent
    content_tsvector = Column(TSVECTOR)  # TSVECTOR column for full-text search
