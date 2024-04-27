from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:root@localhost/discord_db"

    class Config:
        env_file = ".env"

settings = Settings()
