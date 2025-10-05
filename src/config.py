from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./agent_builder.db"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_username: str = ""
    redis_password: str = ""

    # LLM API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Application
    session_expiry_seconds: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
