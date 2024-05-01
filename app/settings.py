from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Application"  # Default value
    profiling: bool = False  # Default is profiling off
    profile_interval: float = 0.01  # Default profiling interval

    class Config:
        env_file = ".env"  # Specifies that settings should be loaded from a .env file
        env_file_encoding = 'utf-8'  # Encoding of the .env file


settings = Settings()  # This instance will be used throughout the application


def get_settings() -> Settings:
    return settings
