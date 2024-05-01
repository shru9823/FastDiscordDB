from pydantic_settings import BaseSettings

# Define a class to hold configuration settings using Pydantic,
# which supports automatic loading from environment variables and .env files.
class Settings(BaseSettings):
    # Define a setting for the database URL with a default value
    # This URL includes the database type, user, password, host, and database name
    database_url: str = "postgresql+asyncpg://postgres:root@localhost/discord_db"

    # Nested Config class for additional configuration settings
    class Config:
        # Specify the path to a .env file that contains environment variables
        env_file = ".env"
        # Enable case sensitivity for environment variable keys,
        # which means that the variable names must match exactly
        case_sensitive = True

# Create an instance of the Settings class
# This instance automatically loads the settings defined above,
# potentially overridden by values from the environment or a .env file
settings = Settings()
