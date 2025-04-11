from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/dbname"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600  # 1 hour
    DB_POOL_TIMEOUT: int = 30

    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # RAG / Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_PORT: Optional[int] = 6333

    # Backend URL (self)
    ARTICLE_CONTROLLER_BACKEND_URL: Optional[str] = None

    # OpenAI / LLM
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
