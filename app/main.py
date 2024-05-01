from fastapi import FastAPI
from .api import chat, search
from .core.database import engine
from .dependencies import startup_redis, shutdown_redis
from .models import Base

app = FastAPI(title="FastDiscordDB")

# Include routers
app.include_router(chat.router)
app.include_router(search.router)

app.add_event_handler("startup", startup_redis)
app.add_event_handler("shutdown", shutdown_redis)
