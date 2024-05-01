from sqlalchemy import Column, String, DateTime, ForeignKey, Date, BIGINT
from sqlalchemy.dialects.postgresql import TSVECTOR
from .core.database import Base  # Importing the Base class from the database core module

class Message(Base):
    __tablename__ = 'discord_chats'  # Name of the table in the database

    # Definitions of columns in the 'discord_chats' table with detailed comments explaining each:

    # The message_id is used as the primary key for this table.
    # It has an index for faster query performance, is of BIGINT type, and cannot be null.
    message_id = Column(BIGINT, primary_key=True, index=True, nullable=False)

    # The channel_id represents the Discord channel from which the message originates.
    # This is also a BIGINT type and cannot be null, ensuring that every message is linked to a channel.
    channel_id = Column(BIGINT, nullable=False)

    # The content column stores the text of the message. It's of type String, which can accommodate varying lengths of text.
    content = Column(String)

    # The message_date stores the date when the message was sent. It is of type Date and is also non-nullable.
    message_date = Column(Date, nullable=False)

    # The content_tsvector column is used for full-text search within PostgreSQL, enhancing search capabilities.
    # It is of type TSVECTOR, which is specific to PostgreSQL and optimizes text search.
    content_tsvector = Column(TSVECTOR)
