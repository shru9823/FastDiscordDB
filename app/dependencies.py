# Importing necessary modules for database and caching functionality
from .core.database import async_session  # Import the async session factory for database operations
import aioredis  # Import the aioredis library for Redis operations

# Define an asynchronous generator to get a database session
# This pattern is typically used in FastAPI to ensure that session cleanup is handled automatically
async def get_db():
    # Establish a context manager for the session to ensure it is closed after use
    async with async_session() as session:
        # Start a new transaction
        async with session.begin():
            # Yield the session to the caller
            yield session

# Global variable for Redis connection; consider using dependency injection for better testability and maintainability
redis = None

# Asynchronous function to set up Redis connection
async def startup_redis():
    global redis  # Access the global variable
    # Initialize the Redis connection with specified URL, set encoding, and enable response decoding
    redis = aioredis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True
    )

# Asynchronous function to cleanly shut down Redis connection
async def shutdown_redis():
    global redis  # Access the global variable
    await redis.close()  # Close the Redis connection

# Asynchronous function to retrieve the Redis connection
async def get_redis():
    # Check if the global Redis connection is already initialized
    if redis is None:
        await startup_redis()  # Start up Redis if not already running
    return redis  # Return the Redis connection
