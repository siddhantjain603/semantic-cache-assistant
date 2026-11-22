
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Semantic Cache Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    REDIS_URL: str = "redis://localhost:6379"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    CACHE_NAME: str = "semantic-cache-assistant"
    CACHE_DISTANCE_THRESHOLD: float = 0.60
    CACHE_TTL: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
