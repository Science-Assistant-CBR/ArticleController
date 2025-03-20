from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/dbname"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600  # 1 hour
    DB_POOL_TIMEOUT: int = 30
    # JWT
    JWT_SECRET_KEY: str = "news-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # RAG
    QDRANT_URL: str
    QDRANT_PORT: Optional[int] = 6333

    class Config:
        env_file = ".env"


settings = Settings()
