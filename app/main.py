from fastapi import FastAPI
from .api import chat, search
from .core.database import engine
from .models import Base

app = FastAPI(title="FastDiscordDB")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(chat.router)
app.include_router(search.router)
