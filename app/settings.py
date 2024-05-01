from pydantic_settings import BaseSettings

# Define a class to manage application settings with type annotations and default values
class Settings(BaseSettings):
    app_name: str = "FastAPI Application"  # Default application name
    profiling: bool = False  # Flag to enable or disable profiling, disabled by default
    profile_interval: float = 0.01  # Default interval between profile samples if profiling is enabled

    # Inner class to configure the behavior of the settings model
    class Config:
        env_file = ".env"  # Path to the environment file that overrides default values
        env_file_encoding = 'utf-8'  # Character encoding for reading the .env file

# Create an instance of the Settings class
# This instance reads configuration from environment variables and the specified .env file
settings = Settings()

# Function to retrieve the current settings instance
# This function can be used to access the settings throughout the application
def get_settings() -> Settings:
    return settings  # Returns the singleton instance of the settings object
