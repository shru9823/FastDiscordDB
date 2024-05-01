# Updated import for declarative_basefrom .config import settings
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = sessionmaker(autocommit=False, autoflush=False,
                             bind=engine, class_=AsyncSession)

Base = declarative_base()
