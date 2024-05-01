from fastapi import FastAPI
# Importing API modules for chat and search functionality
from .api import chat, search
# Importing the database engine object
from .core.database import engine
# Importing startup and shutdown functions for Redis
from .dependencies import startup_redis, shutdown_redis
# Importing the Base class for database models from models module
from .models import Base

# Create an instance of the FastAPI class
# This instance is configured with a title to describe the application
app = FastAPI(title="FastDiscordDB")

# Include routers from the chat and search modules
# Routers manage different sets of endpoints within the application
app.include_router(chat.router)  # Including the chat router that handles chat-related endpoints
app.include_router(search.router)  # Including the search router that handles search-related endpoints

# Add event handlers for application startup and shutdown
# These handlers are functions that perform tasks at application startup and shutdown
app.add_event_handler("startup", startup_redis)  # Adds a startup event handler to initialize Redis
app.add_event_handler("shutdown", shutdown_redis)  # Adds a shutdown event handler to cleanly close Redis connections
