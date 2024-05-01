from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:root@localhost/discord_db"

    class Config:
        env_file = ".env"
        case_sensitive = True  # Ensuring case sensitivity for environment variables


settings = Settings()
