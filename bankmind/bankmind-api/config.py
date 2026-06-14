from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://bankmind:bankmind_secret@localhost:5432/bankmind_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 8

    # Anthropic
    anthropic_api_key: str = ""

    # App
    frontend_url: str = "http://localhost:5173"
    demo_banker_email: str = "admin@bankmind.ai"
    demo_banker_password: str = "demo123"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
