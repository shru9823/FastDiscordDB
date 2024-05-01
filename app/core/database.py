# Import necessary SQLAlchemy components and application settings
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings  # Import application settings from the config module

# Retrieve the database URL from the settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create an asynchronous engine that will use the provided database URL
# The 'echo' parameter is set to True to log all the SQL executed by the engine to the standard output
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Configure the sessionmaker to create AsyncSession instances, not committing automatically
# and not flushing automatically on each query execution
async_session = sessionmaker(autocommit=False, autoflush=False,
                             bind=engine, class_=AsyncSession)

# Create a declarative base class for defining database models
# This class will later be inherited by actual database model classes
Base = declarative_base()
